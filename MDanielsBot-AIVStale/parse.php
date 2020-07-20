<?php
/*
MIT License

Copyright (c) 2018 SQL at the English Wikipedia ( https://en.wikipedia.org/wiki/User:SQL )

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. */

//Master SQLBot switch
// include( "/data/project/botwatch/sqlbot-run.php" );
include( "/data/project/mdanielsbot/credentials.php" );

//Config
$displayNames = FALSE; //Display editor names in the edit summary
$targetPage = "Wikipedia:Administrator intervention against vandalism"; //Target Page
$stopPage = "User:MDanielsBot/AIVStop"; //Page to edit to stop the bot. Change "go" to anything other than go.
$timeLimit = 6; //Time limit in hours

//Coming changes to the time limit. Time floor at 80 admins - 4 hours. Time max at 40 admins - 8 hours. 
//Basically, each admin is worth 6 mins. If $admins is > 60, each whole admin subtracts 6 mins until we get to 80, or +20.
//If $admins is < 60, each whole admin adds 6 mins until we get to 40, or -20.

function choosedb() {
    $web = "enwiki.web.db.svc.eqiad.wmflabs";
    $analytics = "enwiki.analytics.db.svc.eqiad.wmflabs";

    $ts_pw = posix_getpwuid(posix_getuid());
    $ts_mycnf = parse_ini_file($ts_pw['dir'] . "/replica.my.cnf");

    $webtest = mysqli_connect( $web, $ts_mycnf['user'], $ts_mycnf['password'], 'heartbeat_p' );
    $analyticstest = mysqli_connect( $analytics, $ts_mycnf['user'], $ts_mycnf['password'], 'heartbeat_p' );

    $lagq = "select lag from heartbeat where shard = 's1';";

    $lag_wr = mysqli_query( $webtest, $lagq );
    $lag_ar = mysqli_query( $analyticstest, $lagq );

    $lag_webrow = mysqli_fetch_assoc( $lag_wr );
    $lag_anarow = mysqli_fetch_assoc( $lag_ar );

    $weblag = $lag_webrow['lag'];
    $analag = $lag_anarow['lag'];

    if( $weblag < 600 ) {
            $dbhost = $web;
    } elseif ( $weblag <= $analag ) {
        $dbhost = $web;
    } elseif( $analag <= $weblag ) {
        $dbhost = $analytics;
    } else {
        $dbhost = $web;
    }
    mysqli_close( $webtest );
    mysqli_close( $analyticstest );
    return( $dbhost );
}
$dbhost = choosedb();

$adminQuery = 'SELECT count( distinct rc_actor ) as active
FROM recentchanges
join actor on rc_actor = actor_id
INNER JOIN user_groups ON ug_user = actor_user
WHERE rc_timestamp > now() - interval 1 hour
        AND ug_group = "sysop";';
$ts_pw = posix_getpwuid(posix_getuid());
$ts_mycnf = parse_ini_file($ts_pw['dir'] . "/replica.my.cnf");


$mysqli = mysqli_connect( $dbhost, $ts_mycnf['user'], $ts_mycnf['password'], 'enwiki_p' );

if (mysqli_connect_errno()) {
    printf("Connect failed: %s\n", mysqli_connect_error());
    exit();
}

$result = mysqli_query( $mysqli, $adminQuery );
$row = $result->fetch_array( MYSQLI_ASSOC );
mysqli_close( $mysqli );
$adminsActive = $row['active'];

echo "Active admins: $adminsActive\n";

$active = $adminsActive;

$diff = abs( round( 60 - $active, 0 ) );
if( $diff > 20 ) { $diff = 20; }
$offset = ( $diff * 6 ) / 60;
if( $active < 60 ) {
    $timeLimit = $timeLimit + $offset;
} elseif( $active > 60 ) {
    $timeLimit = $timeLimit - $offset;
}
echo "Stale time is at $timeLimit based on $active active in the last hour. diff is $diff and offset is $offset.\n";
$extraES = " Stale time is at $timeLimit hours, see [[User:SQL/AIVStale|Explanation]].";


$cookies = tempnam( '../cookies/', 'cookie.txt' );
$loginurl = "https://en.wikipedia.org/w/api.php?format=json&action=query&meta=tokens&type=login&format=json";

$endPoint = "https://en.wikipedia.org/w/api.php";

function getLoginToken() {
    global $cookies;
    global $endPoint;

    $params1 = [
        "action" => "query",
        "meta" => "tokens",
        "type" => "login",
        "format" => "json"
    ];

    $url = $endPoint . "?" . http_build_query( $params1 );

    $ch = curl_init( $url );
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    curl_setopt( $ch, CURLOPT_COOKIEJAR, $cookies );
    curl_setopt( $ch, CURLOPT_COOKIEFILE, $cookies );

    $output = curl_exec( $ch );
    curl_close( $ch );

    $result = json_decode( $output, true );
    return $result["query"]["tokens"]["logintoken"];
}

function getCsrfToken() {
    global $cookies;
    global $endPoint;

    $params1 = [
        "action" => "query",
        "meta" => "tokens",
        "type" => "csrf",
        "format" => "json"
    ];

    $url = $endPoint . "?" . http_build_query( $params1 );

    $ch = curl_init( $url );
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    curl_setopt( $ch, CURLOPT_COOKIEJAR, $cookies );
    curl_setopt( $ch, CURLOPT_COOKIEFILE, $cookies );

    $output = curl_exec( $ch );
    curl_close( $ch );

    $result = json_decode( $output, true );
    return $result["query"]["tokens"]["csrftoken"];
}
// Step 2: POST request to log in. Use of main account for login is not
// supported. Obtain credentials via Special:BotPasswords
// (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
function loginRequest( $logintoken ) {
    global $cookies;
    global $endPoint;
    global $user;
    global $password;

    $params2 = [
        "action" => "login",
        "lgname" => $user,
        "lgpassword" => $password,
        "lgtoken" => $logintoken,
        "format" => "json"
    ];

    $ch = curl_init();

    curl_setopt( $ch, CURLOPT_URL, $endPoint );
    curl_setopt( $ch, CURLOPT_POST, true );
    curl_setopt( $ch, CURLOPT_POSTFIELDS, http_build_query( $params2 ) );
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    curl_setopt( $ch, CURLOPT_COOKIEJAR, $cookies );
    curl_setopt( $ch, CURLOPT_COOKIEFILE, $cookies );

    $output = curl_exec( $ch );
    curl_close( $ch );
}

function getPage( $pageName )
{
    $pageName = urlencode( $pageName );
    $in = json_decode( file_get_contents( "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=$pageName&rvprop=content&formatversion=2&format=json" ), TRUE );
    $content = $in['query']['pages']['0']['revisions']['0']['content'];
    return ( ltrim( rtrim( $content ) ) );
}
function getLineDate( $line )
{
    $dateregex = "/(\d\d:\d\d, (?:\d\d|\d) (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?) 20\d\d \(UTC\))(?:$| \<\!\-\- Marked \-\-\>$|<\/small> <!--Autosigned by SineBot-->)/i";
    preg_match( $dateregex, ltrim(rtrim( $line )), $matches );
    
    if ( @isset( $matches[1] ) )
    {
        return ( $matches[1] );
    }
}

if ( getPage( $stopPage ) != "go" )
{
    die( "Stop page $stopPage says stop!\n" );
}

function putPage ( $page, $text, $summary ) {
    global $cookies;
    global $csrftoken;
    $login = array();
    $login['text'] = $text;
    $login['token'] = $csrftoken;
    $login['title'] = $page;
    $login['summary'] = $summary;
    $loginurl = "https://en.wikipedia.org/w/api.php?format=json&action=edit";
    $ch = curl_init( $loginurl );
    $postString = http_build_query( $login, '', '&' );
    curl_setopt( $ch, CURLOPT_POST, 1 );
    curl_setopt( $ch, CURLOPT_COOKIEJAR, $cookies );
    curl_setopt( $ch, CURLOPT_COOKIEFILE, $cookies );
    curl_setopt( $ch, CURLOPT_POSTFIELDS, $postString );
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, TRUE );
    $response = curl_exec( $ch );
    curl_close( $ch );
    $reply = json_decode( $response, TRUE );
    print_r( $reply );
    return( $reply );
}

$hours = ( ( $timeLimit * 60 ) * 60 );
//$source = file( "/data/project/botwatch/diff/source.txt" ); //Here for offline testing
//$source = explode( "\n", getPage( "User:MDanielsBot/AIVTest" ) ); //Online testing
$source = explode( "\n", getPage( "Wikipedia:Administrator intervention against vandalism" ) );
$removed = array();
$out = array();
$lastLineWasAReport = FALSE;
$over6Hours = FALSE;
$changed = FALSE;
$numRemoved = 0;
foreach ( $source as $line )
{
    $reportregex = "/\*(?:| )\{\{(?:ip|)vandal(?: |)\|(.*?)\}\}/i";
    preg_match_all( $reportregex, $line, $matches );
#print_r( $line );
    if ( !empty( $matches[1] ) && getLineDate( $line ) != "" )
    {
        $vandal = $matches[1][0];
        $reported = getLineDate( $line );
        $rawtime = strtotime( $reported );
        $diff = time() - $rawtime;
        if ( $diff > $hours )
        {
            $removeit = "!!!REMOVE >6HRS!!!";
            $over6Hours = TRUE;
            $changed = TRUE;
            array_push( $removed, $vandal );
            $numRemoved++;
        }
        else
        {
            $removeit = "";
            $over6Hours = FALSE;
        }
        echo "* Vandal $vandal was reported at $reported, $diff seconds ago! $removeit\n";
        $lastLineWasAReport = TRUE;
    }
    else
    {
        $lastLineWasAReport = FALSE;
#        echo "Last line wasn't a report!\n";
    }
    if ( $over6Hours == FALSE )
    {
        array_push( $out, ltrim( rtrim( $line ) ) );
    }
}
$toFile = implode( "\n", $out );
$page = $targetPage;
$summary = "BOT: Removing Stale AIV Reports. [[Wikipedia:Bots/Requests_for_approval/MDanielsBot 4|BRFA]].$extraES";
$text = $toFile;
$logintoken = getLoginToken(); // Step 1
loginRequest( $logintoken ); // Step 2
$csrftoken = getCsrfToken();
if( $numRemoved > 0 ) {
    putPage( $targetPage, $text, $summary );
}
// putPage( "User:SQL/ActiveAdmins", $adminsActive, "BOT: Updating active Admins" );
?>