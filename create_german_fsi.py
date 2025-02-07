#    Create selected German FSI course notes
#    Copyright (C) 2024 Ray Griner (rgriner_fwd@outlook.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

"""Create selected German FSI course notes."""

#------------------------------------------------------------------------------
# File:    create_german_fsi.py
# Date:    10/17/2020
# Author:  Ray Griner
# Purpose: Create file of selected notes from the German Foreign Service
#   Institute courses. Most notes adhere to a small set of patterns for
#   generating the answer from the prompt and question template, so the prompts
#   and question templates are read in separately and then merged with the
#   answer created automatically to reduce the chance of typos.
# Changes:
# [No change history prior to 20250204]
# [20250204] Minor clean-up for public repository.
# [20250207] Add KEEP_ORIGINAL_TEXT variable to easily switch back and forth.
#   between original text from 1960 and the spelling updates / replacement of
#   out-of-date words.
# [20250207] Remove Model.Qparto column. This was used to override the value
#   of Qpart after merge, but there's no reason Qpart can't be simply set
#   to the right values in Model and Notes, and this change has been done.
#------------------------------------------------------------------------------
import os
import pandas as pd
import numpy as np

#------------------------------------------------------------------------------
# Set to True to use the text from the original publication. Otherwise, the
# columns containing spelling corrections and that replace the words
# 'Fräulein', 'Taxe', 'Schreibmaschine' are used
#------------------------------------------------------------------------------
KEEP_ORIGINAL_TEXT = False
#KEEP_ORIGINAL_TEXT = True

notes_file = os.path.join('input','Notes.txt')
model_file = os.path.join('input','Model.txt')
pattern_file = os.path.join('input','FillPatt_R1.txt')
output_data_file = os.path.join('output','German-FSI-Grammar.txt')
output_fields_file = os.path.join('output','German-FSI-Grammar_fields.txt')

# Notes: The output file is one record per note, as is this input file.
# It contains Prompt2 (the second prompt) for the note, where the first
# prompt comes from the model sentence. It also has response fields that
# will be used to generate the Answer for the note. (Depending on the
# fill pattern, the answer may be a response field unmodified, or it
# might be obtained by substituting the reponse fields into placeholders
# of the `Pattern`.)

notesdf = pd.read_csv(notes_file, sep='\t', header=0, na_filter=False,
                      quoting=3)

# Model: Contains the model sentence used for each note. For
# `FillPatt` from 1 to 4, the model sentence will generate multiple
# notes (say, 8-12 notes per model) using the `Pattern` variable and
# various other variables. The prompts for each model are all adjacent
# to each other in the text. When `FillPatt` is 5 or 6, then each
# model sentence generates only one note.
#
# FillPatt values 1-4 differ in how prompts and answers are generated and
# whether all things to be substituted in the generated prompt are underlined.
# When `FillPatt` is 5 or 6, the response is either a whole sentence
# (FillPatt=5) or two whole sentences that will be seperated by
# an HTML page break (FillPatt=6) and these responses are not underlined.

modeldf = pd.read_csv(model_file, sep='\t', header=0, na_filter=False,
                      quoting=3)

# For use only when `FillPatt == 1`. Use `Notes.R1` to look-up `PrePrompt`, a
# prefix to Prompt2 in the sense described below. The general idea is that
# the desired answer is some determiner + noun. Therefore, to generate the
# note, `Notes.Prompt2` will contain only the noun, `R1` will be the
# determiner in the answer (sometimes followed by another word like an
# adjective), and the final Prompt2 in the output will be set to
# `PrePrompt` + Notes.Prompt2 with the F1 in the model pattern set to blank.
#
# This lookup was created as later models using this pattern may have
# different determiners for different notes in the same model (eg, 'mein' for
# the first note, 'ihr' for the next, etc...), and the same determiners may
# appear in multiple notes (for the same or different models), so this lookup
# table just reduces the possibility of error by creating the determiner
# prompt for each note by hand.
#
# Example: Notes.Prompt2 = 'Bier', Notes.R1 = 'das', so the lookup gives
# PrePrompt = 'd -', and the Prompt2 for the output is 'd- Bier'.
predf = pd.read_csv(pattern_file, sep='\t', header=0, na_filter=False,
                    quoting=3)

notesdf['SortOrder'] = range(0, len(notesdf))

grouplist = ['Unit','Qtype','Qpart','Qnum','Qlet']

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

def fmtnum(x):
    if abs(x - int(x)) < 0.001: x=int(x)
    xstr=f'{x}'
    return xstr

if KEEP_ORIGINAL_TEXT:
    predf['R1'] = np.where(predf.Orig_R1 != '', predf.Orig_R1, predf.R1)
    predf['PrePrompt'] = np.where(predf.Orig_PrePrompt != '',
                                  predf.Orig_PrePrompt, predf.PrePrompt)
    modeldf['Pattern'] = np.where(modeldf.Orig_Pattern != '',
                                  modeldf.Orig_Pattern, modeldf.Pattern)
    modeldf['ModF1'] = np.where(modeldf.Orig_ModF1 != '',
                                  modeldf.Orig_ModF1, modeldf.ModF1)
    modeldf['ModF2'] = np.where(modeldf.Orig_ModF2 != '',
                                  modeldf.Orig_ModF2, modeldf.ModF2)
    notesdf['Prompt2'] = np.where(notesdf.Orig_Prompt2 != '',
                                  notesdf.Orig_Prompt2, notesdf.Prompt2)
    notesdf['R1'] = np.where(notesdf.Orig_R1 != '',
                             notesdf.Orig_R1, notesdf.R1)
    notesdf['R2'] = np.where(notesdf.Orig_R2 != '',
                             notesdf.Orig_R2, notesdf.R2)
else:
    predf['Pre_Modified'] = (predf.Orig_PrePrompt != '')
    # ModF1 is always replaced by blanks when FillPatt == 1 below,
    # so we should not mark the note as modified from the original if
    # only this field has a modification.
    modeldf['Model_Modified'] = ((  (modeldf.Orig_ModF1 != '')
                                  & (modeldf.FillPatt != 1))
                               | (modeldf.Orig_ModF2 != '')
                               | (modeldf.Orig_Pattern != ''))
    notesdf['Note_Modified'] = ((notesdf.Orig_Prompt2 != '')
                              | (notesdf.Orig_R1 != '')
                              | (notesdf.Orig_R2 != ''))

#------------------------------------------------------
# 0. Pre-processing
#------------------------------------------------------
modeldf['FillPatt'] = modeldf.FillPatt.astype('str')
nofill = modeldf[modeldf['FillPatt']=='']
if len(nofill):
    print('ERROR: All rows in Model.txt must have FillPatt populated')
    print(nofill)

#------------------------------------------------------
# 1a. Verify Unit+Qtype+Qnum are a unique key on modeldf
#------------------------------------------------------
dups = modeldf.duplicated(subset=['Unit','Qtype','Qpart','Qnum'])
if dups.any():
    print('ERROR: Duplicate rows in Model.txt')
    print(modeldf[dups])
    exit()

dups = predf.duplicated(subset=['R1'])
if dups.any():
    print('ERROR: Duplicate rows in ' + pattern_file)
    print(predf[dups])
    exit()

dupnote = notesdf.duplicated(subset=['Id'])
if dupnote.any():
    print('ERROR: Duplicate rows in ' + notes_file)
    print(notesdf[dupnote])
    exit()

#------------------------------------------------------
# 2. Merge the datasets and ensure there are no records
#   in one not in the other and vice-versa
#------------------------------------------------------
df = pd.merge(notesdf, modeldf, how='outer',
              on=['Unit','Qtype','Qpart','Qnum'], indicator='whichset')

left_not_right = df[df['whichset']=='left_only']
right_not_left = df[df['whichset']=='right_only']

if len(left_not_right):
    print('ERROR: Row(s) in Notes.txt not in Model.txt')
    print(left_not_right)

if len(right_not_left):
    print('ERROR: Row(s) in Model.txt not in Notes.txt')
    print(right_not_left)

df = df[df['whichset']=='both']

#-------------------------------------------------------------
# 2b. Derive variables
#-------------------------------------------------------------

#------------------------------------------------------------------------------
# Most of the time, Qnum is a unique key (within Unit+Qtype+Qpart).  However,
#  a few conversion drills have multiple prompts for a given Qnum, so in
#  Model.txt and Notes.txt I number them x.1, x.2, ...  Here, I take the floor
#  so that Qnum is again unique
#------------------------------------------------------------------------------
df['Qnum'] = np.floor(df.Qnum)

#------------------------------------------------------------------------------
# Qparto are records where we 'override' the Qpart after the merge. These only
# need to be on modeldf Records with Qparto=missing have sequential values
# of Qnum (i.e., Qnum doesn't restart at 1 when the Part changes). For this
# reason, I didn't both updating the Notes file.
#------------------------------------------------------------------------------
#df['Qpart'] = np.where(df['Qparto']=='', df['Qpart'], df['Qparto'])

###df.sort_values(grouplist)
df['Qseq'] = df.groupby(grouplist).cumcount()
df['grpsize'] = df.groupby = df.groupby(grouplist)['Prompt2'].transform('size')
df['pnumstr'] = np.where(df.grpsize==1, '', df.Qseq.map('.{}'.format)) # pylint: disable=consider-using-f-string
df['NOTE_ID'] = 'FSIDE' + df['Id'].map('{:04x}'.format).str.upper()    # pylint: disable=consider-using-f-string

df['Tags'] = ('U' + df['Unit'].map('{:02}'.format) + ' '               # pylint: disable=consider-using-f-string
        + df['Qtype'] + df['Qpart'] + ' Q' + df['Qnum'].map(fmtnum) + df.Qlet
        + df.pnumstr)
#print(df)

#-------------------------------------------------------------
# 3. Merge to get the prefixes for the prompt for FillPatt==1
#-------------------------------------------------------------
df = pd.merge(df.drop(columns='whichset'), predf, how='outer', on=['R1'],
              indicator='whichset')
df['Tags'] = np.where(df.Note_Modified | df.Model_Modified | df.Pre_Modified,
                      df.Tags + ' Modified', df.Tags)

left_not_right_P1 = df[(df.whichset=='left_only') & (df.FillPatt=='1')]
if len(left_not_right_P1):
    print('ERROR: Row(s) in Notes.txt not in FillPatt_R1.txt')
    print(left_not_right_P1)

right_not_left = df[df['whichset']=='right_only']
if len(right_not_left):
    print('ERROR: Row(s) in FillPatt_R1.txt not in Notes.txt')
    print(right_not_left)

df['ModF1'] = np.where(df['ModF1']=='', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp',
                       df['ModF1'])
df['ModF2'] = np.where(df['ModF2']=='', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp',
                       df['ModF2'])
df['ModF3'] = np.where(df['ModF3']=='', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp',
                       df['ModF3'])

df['IntR1'] = np.where(df['FillPatt']=='1',
                       df['R1'] + ' ' + df['Prompt2'], df['R1'])
df['IntR1'] = np.where(df['FillPatt']=='6',
                       df['IntR1'] + '<br>' + df['R2'], df['IntR1'])
df['Prompt2'] = np.where(df['FillPatt']=='1',
                         df['PrePrompt'] + ' ' + df['Prompt2'], df['Prompt2'])
df['Prompt2'] = df.Prompt2.str.strip()
df['ModF1'] = np.where(df['FillPatt']=='1',
                       '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp', df['ModF1'])

#print(df)

def process_file(pattern, mod_f1, mod_f2, mod_f3, int_r1, r2, r3, fill_patt):
    # In the example sentence, F1 is always underlined.
        # F2/F3 are not underlined for FillPatt=4
    example = pattern.replace('{F1}', '<u>' + mod_f1 + '</u>')
    if fill_patt not in ['4']:
        example = example.replace('{F2}', '<u>' + mod_f2 + '</u>')
        example = example.replace('{F3}', '<u>' + mod_f3 + '</u>')
    else:
        example = example.replace('{F2}', mod_f2)
        example = example.replace('{F3}', mod_f3)

    if fill_patt not in ['5','6']:
        answer = pattern.replace('{F1}', '<u>' + int_r1 + '</u>')
        answer = answer.replace('{F2}', '<u>' + r2 + '</u>')
        answer = answer.replace('{F3}', '<u>' + r3 + '</u>')
    else:
        answer = int_r1

    return (example, answer)

res = []
for row in df[ ['Pattern','ModF1','ModF2','ModF3', 'IntR1',
                'R2','R3','FillPatt']].values:
    res.append(process_file(row[0], row[1], row[2], row[3],
                            row[4], row[5], row[6], row[7]))
df['Prompt1'] = [ x[0] for x in res]
df['Answer'] = [ x[1] for x in res]

#print_full(df['Rules'].value_counts())

ruleList = df['Rules'].unique()
ruleList.sort()
#print(ruleList)

df['Tags'] = df['Tags'] + ' ' + df['Rules']

##df = df.sort_values(['Unit','Qtype','Qnum','Qseq','NOTE_ID'])
df = df.sort_values(['SortOrder'])
df['Qnum'] = df['Qnum'].map(fmtnum)
#print(df)

dfout = df[ ['NOTE_ID','Prompt1','Prompt2','Answer','Unit','Qtype','Qpart',
             'Qnum','Qlet','Qseq','SortOrder','Tags'] ]
#dfout = df[ ['Answer'] ]

# Write the data and variable names to separate files.
dfout.to_csv(output_data_file, sep='\t', index=False, header=False, quoting=3)
dfempty=dfout[0:0]
dfempty.to_csv(output_fields_file, sep='\t', index=False, quoting=3)
