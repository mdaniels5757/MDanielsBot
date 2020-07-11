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

import re

# For when it's inelgible, redundant, or opted out.
GFDL_re = re.compile(u'\{\{GFDL'
                     u'(\-retouched|\-self|\-self\-with\-disclaimers|\-self\-en|'
                        u'\-with-disclaimers|\-en|\-it)?'
                     u'( ?\| ?author ?=[^\|\}]{1,100})?'
                     u'( ?\} ?attribution ?=[^\|\}]{1,100})?'
                     u'( ?\| ?migration ?=[^\|\}]{0,15})?'
                     u'\}\}', re.IGNORECASE | re.UNICODE);

Self_re = re.compile(u'\{\{self2?\|'
                     u'( ?author ?=[^\|]{1,60}\|)?'
                     u' ?GFDL'
                     u'( ?\| ?author ?=[^\|\}]{1,60})?'
                     u'( ?\| ?migration ?=[^\|\}]{0,15})?'
                     u'\}\}', re.IGNORECASE | re.UNICODE);

kettos_re = re.compile(u'\{\{kettős-GFDL-cc-by-sa-2\.5'
                      u'( ?\| ?author ?=[^\|\}]{1,100})?'
                      u'( ?\| ?migration ?=[^\|\}]{0,15})?'
                      u'\}\}', re.IGNORECASE | re.UNICODE);
                      
# For when it's redundant
redundant_re1 = re.compile('\{\{self2?\|( ?author ?=[^\|\}]{1,60}\|)?GFDL\|cc-by-sa-3\.0\}\}'
                          '|\{\{self2?\|( ?author ?=[^\|\}]{1,60}\|)?cc-by-sa-3\.0\|GFDL\}\}',
                           re.IGNORECASE);
                           
redundant_re2 = re.compile('\{\{self2?\|( ?author ?=[^\|\}]{1,60}\|)?GFDL\|cc-by-3\.0\}\}'
                           '|\{\{self2?\|( ?author ?=[^\|\}]{1,60}\|)?cc-by-3\.0\|GFDL\}\}', re.IGNORECASE);
                           
redundant_re3 = re.compile('\{\{self\|( ?author ?=[^\|\}]{1,60}\|)?GFDL\|cc-by-sa-3\.0\,2\.5\,2\.0\,1\.0\}\}'
                           '|\{\{self\|( ?author ?=[^\|\}]{1,60}\|)?cc-by-sa-3\.0\,2\.5\,2\.0\,1\.0\|GFDL\}\}'\
                           , re.IGNORECASE)
            
redundant_re4a = re.compile('\{\{cc\-by(\-sa)?\-(3\.0|2\.0\+|1\.0\+|'
                            '3\.0\,2\.5\,2\.0\,1\.0).*\}\}')                    
redundant_re4b = re.compile('\{\{GFDL(\-author|\-retouched|\-self|'
                           '\-self-with-disclaimers|-self-en|-user|'
                           '-with-disclaimers|-en|\-it|-user-.{2})?\}\}', re.IGNORECASE)
                           
redundant_re5 = re.compile('\{\{self2?\|( ?author ?=[^\|\}]{1,100}\|)?GFDL\|cc-by-sa-([1,2]\.[0,5]\+)\}\}'
                          '|\{\{self2?\|( ?author ?=[^\|\}]{1,100}\|)?cc-by-sa-([1,2]\.[0,5]\+)\|GFDL\}\}',
                           re.IGNORECASE);
                           
# {{Original upload date}}

origUploadDate_re1 = re.compile(u'\{\{Original upload date\|'
                              u'(\d{4})[\-,\|](\d{2})[\-,\|](\d{2})\}\}', re.IGNORECASE | re.UNICODE)