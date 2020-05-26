# Copyright 2020 Michael Daniels
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pywikibot
import re
import MigrationRegexes
import time
from datetime import datetime, timezone
import wikitextparser as wtp

site = pywikibot.Site('commons', 'commons');
categoryName = "Category:License migration candidates";
optOutAutoPage = pywikibot.Page("User:MDanielsBot/LROptOut#List (Automatic)");
optOutManualPage = pywikibot.Page("User:MDanielsBot/LROptOut#List (Manual)");
mustBeBefore = datetime.utcfromtimestamp(1248998400);

# Computes if the file's EXIF data is too new
# Input: the file_info object given by pywikibot
# Returns: the bool photoTooNew, which is true if the photo is too new
#            and false if it is not.
def exif_too_new(file_info):
    file_metadata = file_info["metadata"];
    
    if file_metadata is None: return False;
    
    # else
    datetime_str = next(filter(lambda x: x['name'] == 'DateTime', file_metadata),\
        {'value' : "0000:00:00 00:00:00"})['value'];
    if datetime_str == "0000:00:00 00:00:00":
        return False;
    theDatetime = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S");

    original_datetime_str = next(filter(lambda x: x['name'] == 'DateTime',\
        file_metadata), {'value' : "0000:00:00 00:00:00"})['value'];
    if original_datetime_str == "0000:00:00 00:00:00":
        return False;
    original_datetime = datetime.strptime(original_datetime_str,\
                        "%Y:%m:%d %H:%M:%S");    
    
    photoTooNew = (original_datetime > mustBeBefore\
                  and theDatetime > mustBeBefore);
    
    return photoTooNew;

# Determines if there is an original upload date template. 
#    If there is none, return the string "nonefound"
#    If there is one, and it is too new for relicense, return "ineligible"
#    If there is one, and it shows that the photo is elgible, return eligible".
def process_orig_upload_date(revision):
    text = revision.text;
    
    if not text: return "nonefound";
    
    match = MigrationRegexes.origUploadDate_re1.search(text);
    
    if not match: return "nonefound";
    # else
    origUploadDate_str = ''.join(map(str, match.groups()))
    origUploadDate = datetime.strptime(origUploadDate_str, "%Y%m%d")
    
    if (origUploadDate > mustBeBefore):
        return "inelgible";
    elif (origUploadDate < mustBeBefore):
        return "eligible";
    else:
        return "nonefound";
        
# SHOULD NOT BE USED YET
# Determines if there is an "original upload log" table with the
#     original upload date
#    If there is no wikitable, return the string "nonefound"
#    If there is one, and it is too new for relicense, return "ineligible"
#    If there is one, and it shows that the photo is elgible, return eligible".
def process_orig_upload_log(page):
    
    # I SAID, shouldn't be used yet.
    return "nonefound"
    
    text = page.text;
    p = wtp.parse(text);
    if len(p.tables) == 0: return "nonefound";
    t = p.tables[0];

    col = t.data(column=0);
    if (col[0] != r"{{int:filehist-datetime}}"):
        return "nonefound";
    
    numuploads = len(col) - 1
    if (numuploads > 1): return "nonefound"; # Process these manually for now
    try:
        oldUploadDate = datetime.strptime(col[1], "%Y-%m-%d %H:%M");
        if (oldUploadDate < mustBeBefore):
            return "eligible";
        elif (oldUploadDate > mustBeBefore):
            return "inelgible";
        else:
            return "nonefound";
    except:
        return "nonefound";

# Performs replacements for pages inelgible for license migration
# Input: pywikibot page object
# Returns: True if replacement made, false if not
def migration_inelgible(page):
    text = newtext = page.get();
    
    match = MigrationRegexes.GFDL_re.search(text)
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    '{{GFDL\g<1>\g<2>\g<3>|migration=not-eligible}}',
                    oldstring, re.IGNORECASE
                    );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    match = MigrationRegexes.Self_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    '{{self|\g<1>GFDL|migration=not-eligible}}',
                     oldstring, re.IGNORECASE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);

    match = MigrationRegexes.kettos_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    u'{{kettős-GFDL-cc-by-sa-2.5\g<1>|migration=not-eligible}}',
                     oldstring, re.IGNORECASE | re.UNICODE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    if (newtext != text):
        page.put(newtext, r'[[Commons:License_Migration_Task_Force/Migration'
                         + r'|License Migration]]: not-eligible')
        return True;
    # else
    return False;

# Performs replacements for pages inelgible for license migration
# Input: pywikibot page object
# Returns: True if replacement made, false if not
def migration_relicense(page):
    text = newtext = page.text
    
    match = MigrationRegexes.GFDL_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    u'{{GFDL\g<1>\g<2>\g<3>|migration=relicense}}',
                    oldstring, re.IGNORECASE | re.UNICODE
                    );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    match = MigrationRegexes.Self_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    u'{{self|\g<1>GFDL|migration=relicense}}',
                     oldstring, re.IGNORECASE | re.UNICODE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);

    MigrationRegexes.kettos_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                     u'{{kettős-GFDL-cc-by-sa-2.5\g<1>|migration=relicense}}',
                     oldstring, re.IGNORECASE | re.UNICODE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    if (newtext != text):
        page.put(newtext, r'[[Commons:License_Migration_Task_Force/Migration'
                         + r'|License Migration]]: relicensed')
        return True;
    # else
    return False;

# Computes whether migration would be redundant.
# If so, returns false.
# If not, performs replacements and returns true.
# Input: pywikibot page object
def migration_redundant(page):
    text = newtext = page.text;
    
    redundant_re0 = re.compile('Cc-by-3\.0|Cc-by-sa-3\.0', re.IGNORECASE)
    if (redundant_re0 == None): return False;
    # Otherwise, continue
    
    match = MigrationRegexes.redundant_re1.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.redundant_re1.sub(
                    '{{self|GFDL|cc-by-sa-3.0|\g<1>migration=redundant}}',\
                    oldstring, re.IGNORECASE);
        newtext = newtext.replace(oldstring, newstring, 1);
    
    MigrationRegexes.redundant_re2.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.redundant_re2.sub(
                    '{{self|GFDL|cc-by-3.0|\g<1>migration=redundant}}'\
                    , oldstring, re.IGNORECASE);
        newtext = newtext.replace(oldstring, newstring, 1);
    
    match = MigrationRegexes.redundant_re3.search(text)
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.redundant_re3.sub(
                    '{{self|GFDL|cc-by-sa-3.0,2.5,2.0,1.0'
                    '|\g<1>migration=redundant}}'\
                    , oldstring, re.IGNORECASE);
        newtext = newtext.replace(oldstring, newstring, 1);
    
    if (MigrationRegexes.redundant_re4a.search(text) != None):
        match = MigrationRegexes.redundant_re4b.search(text)
        if match:
            oldstring = match.group(0);
            newstring = MigrationRegexes.redundant_re4b.sub(
                        '{{GFDL\g<1>|migration=redundant}}',
                        oldstring, re.IGNORECASE);
            newtext = newtext.replace(oldstring, newstring, 1);
            
    match = MigrationRegexes.redundant_re5.search(text)
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.redundant_re5.sub(
                    '{{self|\g<1>cc-by-sa-\g<2>|GFDL|migration=redundant}}',
                    oldstring, re.IGNORECASE);
        newtext = newtext.replace(oldstring, newstring, 1);
    
    if (newtext != text):
        page.put(newtext, r'[[Commons:License_Migration_Task_Force/Migration'
                          + r'|License Migration]]: redundant')
        return True;
    
    return False;

# Performs replacements for pages where the uploader opted out.
# Returns true if replacement made, false if not.
def migration_opt_out(page):
    text = newtext = page.text
    
    match = MigrationRegexes.GFDL_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    u'{{GFDL\g<1>\g<2>\g<3>|migration=opt-out}}',
                    oldstring, re.IGNORECASE | re.UNICODE
                    );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    match = MigrationRegexes.Self_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                    u'{{self|\g<1>GFDL|migration=opt-out}}',
                     oldstring, re.IGNORECASE | re.UNICODE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);

    MigrationRegexes.kettos_re.search(text);
    if match:
        oldstring = match.group(0);
        newstring = MigrationRegexes.GFDL_re.sub(
                     u'{{kettős-GFDL-cc-by-sa-2.5\g<1>|migration=opt-out}}',
                     oldstring, re.IGNORECASE | re.UNICODE
                     );
        newtext = newtext.replace(oldstring, newstring, 1);
    
    if (newtext != text):
        page.put(newtext, r'[[Commons:License_Migration_Task_Force/Migration'
                         + r'|License Migration]]: User opted out')
        return True;
    else:
        return False;

# Determines if the page is inelgible for migration
# Input: Page object. Output: bool.
def isInelgible(page):
    oldestFInfo = page.oldest_file_info;
    latestFInfo = page.latest_file_info;
    return ((exif_too_new(latestFInfo) and\
            exif_too_new(oldestFInfo)) or \
            (process_orig_upload_date(page.latest_revision) ==
            "ineligible") or process_orig_upload_log(page) == "ineligible");

# Simple helper function to determine if eligible for migration.
# Input: Page object. Output: bool.
def isEligible(page):
    return (process_orig_upload_date(page.latest_revision) == "eligible" or\
          process_orig_upload_log(page) == "eligible")

# Return 1 if user is opted out manually, 2 if automatically, 0 if neither.
def isOptedOut(page):
    for link in page.linkedPages(namespaces=2):
        for user in optOutManualPage.linkedPages(namespaces=2):
            if (link == user): return 1;
        for user in optOutAutoPage.linkedPages(namespaces=2):
            if (link == user): return 2;
    
    # If nothing
    return 0;

def main():
    cat = pywikibot.Category(site, categoryName)
    i = 0;
    for page in cat.articles():
        i = i + 1;
        time.sleep(1);
        
        # If the file is redundant, it doesn't matter if it's inelgible.
        if migration_redundant(page):
            # Function already did replacement
            print('Migration redundant, i = {0}.'.format(i))
        elif isInelgible(Page):
            # If the changes succeeded
            if (migration_inelgible(page)):
                print('Migration inelgible, i = {0}.'.format(i));
            # If it failed
            else:
                print("BEGIN PAGE {0} ({1}):".format(i, page.title()))
                print(page.get())
                print("END PAGE {0}".format(i))
                print(('Migration inelgible, but no replacement made!'\
                 + ' (i= {0})').format(i));
        elif (isOptedOut(Page) == 1):
            # User in the Opted out -- manual list
            
            # Was going to perform replacement, but skip for now.
            # migration_opt_out(Page);
            continue;
        elif (isOptedOut(Page) == 2):
            # User in the Opted out -- automatic list
            # Skip (at least for now)
            continue;
        elif isEligible(Page):
                if migration_relicense(page):
                    print('Migration relicensed, i = {0}.'.format(i));
                    continue;
                else:
                    print("BEGIN PAGE {0} ({1}):".format(i, page.title()))
                    print(page.get())
                    print("END PAGE {0}".format(i))
                    print(('Migration elgible, but no replacement made!'\
                     + ' (i= {0})').format(i))
        else:
            print("BEGIN PAGE {0} ({1}):".format(i, page.title()))
            print(page.get())
            print("END PAGE {0}".format(i))
            print(('Nothing to do here? (i= {0})').format(i));
    # End loop

if __name__ == "__main__":
    main();