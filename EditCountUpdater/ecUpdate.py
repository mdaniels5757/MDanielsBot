import pywikibot
import json
from datetime import datetime, timezone

enwiki = pywikibot.Site('en', 'wikipedia');
enLocalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/LocalEC')
enGlobalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/GlobalEC')

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

# Local EC for enwiki
for userpage in enLocalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(enwiki, userpage.title(with_ns=False));
    if (user.groups() == ['*', 'user'] or user.groups() == ['*', 'user', 'autoconfirmed']):
        continue;
    localEC = user.editCount();
    subpage_name = enLocalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(enwiki, subpage_name)
    if subpage.text != localEC:
        subpage.put(localEC, summary="Updating edit count")
    
# Global EC for enwiki
for userpage in enGlobalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(enwiki, userpage.title(with_ns=False));
    if (user.groups() == ['*', 'user'] or user.groups() == ['*', 'user', 'autoconfirmed']):
        continue;
    globalEC = globaleditcount(user);
    subpage_name = enGlobalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(enwiki, subpage_name)
    if subpage.text != globalEC:
        subpage.put(globalEC, summary="Updating edit count")

commonswiki = pywikibot.Site('commons', 'commons');
commonsLocalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/LocalEC')
commonsGlobalTemplatePage = pywikibot.Page(enwiki, 'User:MDanielsBot/GlobalEC')

# Local EC for commonswiki
for userpage in commonsLocalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(commonswiki, userpage.title(with_ns=False));
    if (user.groups() == ['*', 'user'] or user.groups() == ['*', 'user', 'autoconfirmed']):
        continue;
    localEC = user.editCount();
    subpage_name = commonsLocalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(commonswiki, subpage_name)
    if subpage.text != localEC:
        subpage.put(localEC, summary="Updating edit count")
    
# Global EC for commonswiki
for userpage in commonsGlobalTemplatePage.embeddedin(namespaces=2):
    if userpage.depth != 0: continue;
    username = userpage.title(with_ns=False)
    user = pywikibot.page.User(commonswiki, userpage.title(with_ns=False));
    if (user.groups() == ['*', 'user'] or user.groups() == ['*', 'user', 'autoconfirmed']):
        continue;
    globalEC = globaleditcount(user);
    subpage_name = commonsGlobalTemplatePage.title() + '/' + username
    subpage = pywikibot.Page(commonswiki, subpage_name)
    if subpage.text != globalEC:
        subpage.put(globalEC, summary="Updating edit count")