import pywikibot
import json
from datetime import datetime, timezone

def floor(num, roundto):
    return num - (num % roundto);

def globaleditcount(user):
    params = {
    	"action": "query",
    	"format": "json",
    	"meta": "globaluserinfo",
    	"guiuser": user.username,
    	"guiprop": "editcount"
    }
    response = pywikibot.data.api.Request(site=user.site, parameters=params).submit()
    return response['query']['globaluserinfo']['editcount']

enwiki = pywikibot.Site('en', 'wikipedia');
enwiki.login();
enLocalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/LocalEC')
enGlobalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/GlobalEC')

# Local EC for enwiki
for userpage in enLocalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(enwiki, userpage.title(with_ns=False));
    localEC = user.editCount();
    subpage_name = enLocalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(enwiki, subpage_name)
    
    # Only update every 100 edits
    tol = 100;
    localEC = floor(localEC, tol)
        
    if localEC <= 5000 and username != "MDanielsBot":
        continue;
    
    if int(subpage.text) != localEC:
        subpage.put(localEC, summary="Updating edit count")
    
# Global EC for enwiki
for userpage in enGlobalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(enwiki, userpage.title(with_ns=False));
    globalEC = globaleditcount(user);
    subpage_name = enGlobalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(enwiki, subpage_name)
    
    # Only update every 100 edits
    tol = 100;
    globalEC = floor(globalEC, tol)
    
    if globalEC <= 5000 and username != "MDanielsBot":
        continue;
    
    if int(subpage.text) != globalEC:
        subpage.put(globalEC, summary="Updating edit count")

commonswiki = pywikibot.Site('commons', 'commons');
commonsLocalTemplatePage = pywikibot.Page(commonswiki, 'User:MDanielsBot/LocalEC')
commonsGlobalTemplatePage = pywikibot.Page(commonswiki, 'User:MDanielsBot/GlobalEC')

# Local EC for commonswiki
for userpage in commonsLocalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(commonswiki, userpage.title(with_ns=False));
    localEC = user.editCount();
    subpage_name = commonsLocalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(commonswiki, subpage_name)
    
    # Only update every 100 edits
    tol = 100;
    localEC = floor(localEC, tol)
    
    if localEC <= 5000 and username != "MDanielsBot":
        continue;
    
    if int(subpage.text) != localEC:
        subpage.put(localEC, summary="Updating edit count", botflag=True)
    
# Global EC for commonswiki
for userpage in commonsGlobalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(commonswiki, userpage.title(with_ns=False));
    globalEC = globaleditcount(user);
    subpage_name = commonsGlobalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(commonswiki, subpage_name)
    
    # Only update every 100 edits
    tol = 100;
    globalEC = floor(globalEC, tol)
    
    if globalEC <= 5000 and username != "MDanielsBot":
        continue;
    
    if int(subpage.text) != globalEC:
        subpage.put(globalEC, summary="Updating edit count", botflag=True)