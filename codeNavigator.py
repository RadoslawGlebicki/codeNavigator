#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Radoslaw Glebicki
# email: glebicki@o2.pl
# version: 1.02 very beta ;-D
# above lines to read for `About`

# NOTE: codeNavigator

# TODO: regexp in filter field
# TODO: after clear filter field if checkmark (group) is on then must be use this to grouping
# TODO: how get back focus on Kate?

import sys, os, re, json, codecs, html, subprocess, hashlib #, time
from PyQt5.QtWidgets import QComboBox, QLineEdit, QVBoxLayout, QWidget, QPushButton, QApplication
from PyQt5.QtWidgets import QMessageBox, QFrame, QFileDialog, QGroupBox, QPlainTextEdit
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QDialog, QShortcut
from PyQt5.QtWidgets import QCheckBox, QGridLayout, QToolTip, QMenu, QAction
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSizePolicy, QStyleFactory
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QCursor, QIntValidator, QClipboard
from PyQt5.QtCore import QSize, QTimer, Qt

gbDEBUG          = False    # for debug
gsbl             = '\u007b' # left  curly bracket -> {
gsbr             = '\u007d' # right curly bracket -> }
gnLng            = None     # None - before read conf, later: 0 - polski, 1 - English
glListOfConfigs  = []       # list all configs for projects as dict [0]{},[1]{}, etc. [0] current
glCompRegWords   = []       # list of compiled words to search (after re.compile)
glMatchLines     = []       # list all lines contain word/phrase glCompRegWords.
                            # Inside tuplas(line nr, pos. of word, line text)
glMainListBoxLns = []       # only lines showing in main listBox (ex. after filtering or grouping, etc)
glKeysOrder      = ['name','comment','words','file','notes'] # names of keys for json conf USEIN:IUY875
nXbtn, nYbtn     = 22, 3 # pos X, Y for ClearBtn inside filter Input
gsFILE           = os.path.abspath(__file__)
gsSEP            = os.path.sep # depends on system / or \
gsAppDIR         = os.path.abspath(os.path.dirname(__file__)) + gsSEP
gsCONF_FILE      = gsAppDIR + "codeNavigatorConf.json"
gsGO_TO_ANCHOR   = 'Go to anchor: ' # add later
gnTIME_INTERVAL  = 1500 # check for changes in monitored file
gsNOTES_HASH_CURRENT = None # hash for `notes` for diff if closing to ask: save changes?
gsColBkg         = '#333333' # background color for input filter
gsColErr         = "Salmon"
gsColSel         = '#3282ac' # select color for main QListWidget
gnConfWinW       = 400 # Conf width
gnConfWinH       = 100 # fit to elements ??? so not important
gnFSfrom         = 8   # for combo to choose font size from
gnFSto           = 21  # to (range like always -1)
gdAppConf        = {'x':"0",'y':"0",'w':'250','h':None,'fs':"12",'lng':0} # `h` will be set later after oApp starts
gsColSelInLst    = f'QListWidget {gsbl}font-size: {gdAppConf['fs']};{gsbr} QListWidget::item:hover{gsbl}background: {gsColSel};{gsbr}'
gsMenuStyleSheet = f"""QMenu {{border: 1px solid {gsColSel}; background: {gsColBkg}; font-size: {gdAppConf['fs']};}}
						QMenu::item:selected{{ background: {gsColSel}; }}""".replace("\t","")
oQmainFont  = QFont('System', int(gdAppConf['fs']), QFont.Normal)
oQmainFontB = QFont('System', int(gdAppConf['fs']), QFont.Bold)
oQfilterPHTfont = QFont('System', int(gdAppConf['fs']) -1 ) # smaller font for PlaceHolderText

def f_Lng(sKey, bLst = False): # translator function
	""" sKey - string as a key to look in dict for translation list. list pos depends on gnLng
		return back translation in proper language
		bLst - is giving back (if set True) just list of elements for given key
		return mainly `str`, but par. `bLst = True` then ret. `list`"""
	dLng = {
# A
	'AboutAuthor' :['Autor','Author'],
	'AboutEmail'  :['Listel','Email'],
	'AboutVersion':['Wersja','Version'],
	'AboutTxt'    :['Program wspomagający pracę z edytorem Kate.','Program supporting work with Kate editor.'],
	'AboutWinTtl' :['O...','About'],
	'addElmConf'  :["Dod. el.","Add elm."],
	'addElmConfTT':["Umożliwia dodanie\nnowego obiektu","Lets add\nnew element"],
# B
	'belowNotes':["Poniżej są notatki","'Below are notes'"],
	'bigerNotesBackgroundTxt':['Zapisz tu swoje przemyslenia\no kodzie','Write here own thoughts\nabout code'],
	'bigNotesWasChanged'     :["Notatki zostały zmienione!\nPrzenieść je do głównego okna?",
								"Notes was changed!\nTransfer it to main window?"],
	'bigNotesInfoTtl'        :["Notatki zostały zmienione!",'Notes was changed!'],
	'binFile'   :["Plik binarny!!!","Binary file!!!"],
# C
	'chooseLang':['Wybierz język: polski','Choose language: English'],
	'Config':['Ustawienia','Settings'],
	'confNotesEdit':["Aby edytować notatkę to\nw głównym oknie wybierz `Edytuj`",
                     "To edit this note in\nmain window push `Edit`"],
# D
	'def_words'     :['Podaj,tu,swoje,słowa','Put,here,your,words'],
	'delConfWinTtl' :['Uwaga!','Warning!'],
	'delConfMsg'    :['To działanie spowoduje\nusunięcie tego wpisu z listy konfiguracji!\nWykonać?',
					'This action will cause\nerase that entry from configuration list!\nExecute?'],
# E
	'ExitConfWinTtl':["Opuścić konfig.?","Leave config.?"],
	'ExitConfMsg'   :["Naciskając `Tak` utracisz\nwszystkie zmiany!",
					"By pressing `Yes` you\nwill loose all changes!"],
# F
	'fileConf_nCorrect':['Problem z zapisem pliku konfiguracyjnego!','Problem with write to the conf. file!'],
	'File2Mon_Menu'    :["Wybierz konfig.","Chooose config."],
	'fs_label':['R. fontu','Font s.'],
	'f_readConfig_Error':['Tekst błędu: ','Error text: '],
	'file_nCorrect':['Pliku do monitorowania jest nieprawidłowy!\n','File to monitoring is not correct\n'],
	'f_readConfig_ErrTxt':['Plik konfiguracyjny nie istnieje (pierwsze uruchomienie) lub jest uszkodzony! Ustawione zostaną wartości domyślne.',
                           'Configuration file doesn\'t exists (first run) or can be corrupt! Will be set default values.'],
	'f_Err_WinTtl':['Informacja','Information'],
	'f_Err_DefErr':["""Pojawił się błąd. Wiem, że on tu jest. \nNie mogę go wyłapać.
					Proszę, zapamiętaj co zrobiłeś i poinformuj mnie!
					Mój adres email to: glebicki@o2.pl""","""An error occure. I know it is there.\nI cannot catch it.
					Please, remember what you did and inform me!\nMy email address is: glebicki@o2.pl"""],
# G
	"Gotoline":["Idź do: ","Go to: "],
	'Group'   :['Grupuj','Group'],
# H
	'hereAboutCode':["Tutaj jest miejsce na\nnotatki o kodzie","Here is place for\nnotes about code"],
# L
	'Load2Kate'     :['Ładuj do Kate','Load to Kate'],
	'Load2Kate_TT'  :['Ładuj do Kate plik powiązany\nz danymi w oknie.',
                    'Load to Kate file related\nto data in window'],
	'lngDefProgName':['Program domyślny','Default program'],
	'lngDefComment' :['Przykładowy program, gdy pierwsze uruchomienie.',
                     'Default program, for first run.'],
	'lngErrorL0' :['Ta wartość nie może być ujemna!',"This value can`t be negative"],
	'lngFS_TT'   :['Rozmiar czcionki nie może być ujemny!','Font size cannot be negative!'],
	'lngFS_range':['Rozmiar czcionki może być \njedynie w zakresie 8 do 14!','Font size can be only \nin range from 8 to 14'],
	'lngFlToMon_TT'  :['Podaj plik do monitorowania!','Give a file to monitoring!'],
	'lngFlDtExist_TT':['Plik nie istnieje!','File doesn\'t exist!'],
	'lng_sRes_Err1'  :['Błędny RegExp:','Wrong RegExp:'],
	'lng_sRes_Err2'  :['\nPopraw tę frazę!','\nCorrect this phrase!'],
	'lng_lbl':['Język','Lang.'],
	'lang'   :['polski','English'],
	'lng'    :['pl','en'],
# M
	'mainWinEdit'         :["Edytuj","Edit"],
	'mainWinQuitNotesInfo':["Notatki zostały zmienione!\nZapisać je?","Notes was changed!\nSave it?"],
	'Menu':['Menu','Menu'],'About':['O...','About'],
	'm_chooseFile':['Wybierz plik','Choose file'],
	'm_checkConfW_ErrTxt_1':['łędny RegExp: ','rong RegExp: '], # in m_checkConfWordsAsRegExp
	'm_checkConfW_ErrTxt_2':['\nPopraw tę frazę w pliku konf.\nNa teraz zostanie ona odrzucona!','\nChange it in conf file\nNow it was drop off!'],
	'm_tWords_Err1':['Błędny RegExp: ','Wrong RegExp: '],
	'm_tWords_Err2':['\nPopraw tę frazę!','\nCorrect this phrase!'],
# N
	'No'       :['Nie','No'],
	'noKate'   :['Program Kate nie istnieje?!\n',"Program Kate doesn't exist?!\n"],
	'notExists':['\nnie istnieje!',"\ndoesn't exist!"],
	'Notes'    :['Notatki','Notes'],
	'notesEdit':['Edycja notatek','Edit notes'],
# O
	'openConf_MenuTT'  :["Otwiera okno konfiguracji","Open setup window",],
	'openObject_MenuTT':["Otwiera okno wyboru\npliku dla monitorowania","Open window to\nchoose file for monitoring"],
	'oqChBxSort_TT'    :['Grupuje wyrazy/frazy','Grouping words/phrases'],
# P
	'posLbl'       :['Pozycja i wymiary głównego okna oraz r. czcionki (?)','Pos. and dims. for m. window and font size (?)'],
	'posLbl_TT'    :['Podane dane zostaną użyte\nprzy następnym uruchomieniu.','Those data will be use\nduring next start.'],
# Q
	'QConfCombo_ErrTT'     :['Podaj nazwę dla konfiguracji!','Give the name for config!'],
	'QConfCombo_NmExistsTT':['Błąd: Nazwa istnieje!','Error: name exists!'],
	'QConfComboCnxMnuClean':["Czyść pola","Clear fields"],
	'QCommLab'     :['Komentarz','Comment'],
	'QConfDelBtn'  :['Kasuj','Del'],
	'QConfDelTT'   :["Kasuje aktualną\nkonfigurację","Delete current\nconfiguration"],
	'QConfResetBtn':["Czyść","Reset"],
	'QConfResetTT' :["Tylko czyści pola","Cleaning fields only"],
	'QConfLiLbl'   :['Lista konfiguracji','Configurations list'],
	'QConfLiLbl_TT':["Wybierz konfigurację z listy.",
					"Choose configuration from the list."],
	'QConfWinTtl'  :['Konfiguracja','Configuration'],
	'QConfWords_TT':['Każda spacja ma znaczenie!\n'
					'Przecinki dla RegExp poprzedzaj backslashem "\\".\n'
					'Słowa dla Kate to: NOTE,BEGIN,TODO, i inne\n'
					'a dla języka prg.: function,def,class, itp.',
					'Each space is important\n'
					'Commas for RegExp follow backslash "\\".\n'
					'Words for Kate are: NOTE,BEGIN,TODO, and more\n'
					'and for prg. language: function,def,class, etc.'],
	'QConfWordsLbl'   :['Wyszukiwane wyrazy/frazy (?)','Searched words/phrases (?)'],
	'QConfWordsBtn'   :['Test ','Test '],
	'QConfWordsBtn_TT':['Możesz testować czy zawarte\nfrazy RegExp są poprawne (ERE)',
                        'Test if words/phrases\nare correct as RegExp (ERE)'],
	'QConfFileLbl'    :['Plik do monitorowania','File for monitoring'],
	'QConfReadFileBtn':[' Plik ',' File '],
	'QBtnSave'       :['Zapisz','Save'],
	'QBtnCancel'     :['Anuluj','Cancel'],
	'Quit'      :['Zakończ','Quit'],
	'Quit_TT'   :["Wyjście z programu","Exit from program"],
# S
	'sNext1'    :['B','W'],
	'sNext2'    :['Kolejny b','Next w'],        # connected with lower line in `m_checkConfW_ErrTxt_1`
# T
	'takeBtn'   :['Weź ','Take '],
	'takeBtn_TT':['Pobiera aktualną pozycję\ni wymiary głównego okna','Taking actual position\nand dimensions of main window'],
	'TTfilter'  :['Filtruje listę. Dla `lub`\nwstaw `|` pomiędzy wyrazy (bez spacji)',
                'Filtering list. For `or`\ninsert `|` between words (without spaces)'],
# Y
	'Yes'       :["Tak","Yes"],
	}
	if gnLng == None: nLng = 1
	else: nLng = gnLng
	if bLst:
		return dLng[sKey]
	return dLng[sKey][nLng].replace("\t","")
def f_strToList(sStr):                  # Func. divide on comas
	# Func. divide on comas, but only if this coma is not for regexp with \
	# this to split "," , but not this "\,"
	nWordStart = 0
	lWordsList = []
	for i in range(len(sStr)):
		if i == 0: continue
		if sStr[i] == ',': # coma found
			if sStr[i-1] != "\\": # befor coma is backslash
				lWordsList += [sStr[nWordStart:i]]
				nWordStart = i + 1
	lWordsList += [sStr[nWordStart:len(sStr)]]
	return lWordsList
def f_liveEntry(sTxtInInputField):      # Filtering after each letter
	global  glMainListBoxLns
	if sTxtInInputField != '':
		oqFilterInput.setFont(oQmainFont)
		reString = re.compile(sTxtInInputField.lower())
		lFiltered = list(filter(lambda x: re.search(reString,x[2].lower()), glMatchLines))
		glMainListBoxLns = f_fillListBox(lFiltered)
	else:
		oqFilterInput.setFont(oQfilterPHTfont)
		glMainListBoxLns = f_fillListBox(glMatchLines)
	return None
def f_Error(sErrorTxt = '', oParent = None):       # open dialog with info or error
	if sErrorTxt == '': sErrorTxt = f_Lng('f_Err_DefErr') # Default text for error
	
	qErrWin = QMessageBox(oParent)
	try: qErrWin.setFont(oQmainFont)
	except: qErrWin.setFont(oQmainFont)
	qErrWin.setIcon(QMessageBox.Warning)
	qErrWin.setText(sErrorTxt)
	qErrWin.setWindowTitle(f_Lng('f_Err_WinTtl'))
	qErrWin.setStandardButtons(QMessageBox.Ok)

	qErrWin.exec()
	return None
def f_fillListBox(lArray):              # fill main listWidget with choosen lines
	"""Fill main listBox with lines from lArray
	and return list to remember what is in main listBox"""
	lReturn = []
	oQlist.clear() # clear listBox
	for idx,line in enumerate(lArray):
		qItem = QListWidgetItem(line[2][line[1]:])
		qItem.setToolTip(html.escape(str(line[0]) + " " + line[2]))
		oQlist.addItem(qItem)
		lReturn.append(line)
	return lReturn
def f_lineSelect(qItem):                # go to line in Kate
	"""from parent widget from qItem get row/currentItem and then index: nIdx"""
	nIdx = qItem.listWidget().row(qItem.listWidget().currentItem())
	os.system(f"kate -l {glMainListBoxLns[nIdx][0]}")
	return None
def f_Interval():                       # checking if file was c_hanged. Maybe is better way?
	'''Each gnTIME_INTERVAL in ms (1500ms def) this func is called and check
	if monitored file was changed'''
	global gsFILE_TIME, glMatchLines, glMainListBoxLns
	try:
		sChange = os.stat(glListOfConfigs[0]['file']).st_mtime
	except:
		print("f_Interval: No file to read")
		return None
	if sChange != gsFILE_TIME:
		gsFILE_TIME = sChange
		glMatchLines = f_readFile(glListOfConfigs[0]['file'])
		if oqFilterInput.text() != '':
			f_liveEntry(oqFilterInput.text())
		if oqFilterInput.text() == '':
			glMainListBoxLns = f_fillListBox(glMatchLines)
		if oqChBxSort.checkState() == 2:
			f_ChBtGroup(True) #
	return None
def f_checkIfInclude(sLine):      # checking if given line has regEx from list `glCompRegWords` processed by `re.compile`
	for elm in glCompRegWords:
		oReg = elm.search(sLine)
		if oReg != None:
			return oReg.start() # column of first match
	return -1
def f_readFile(sFile):                  # read file for monitoring
	""" Read default file [0] from glListOfConfigs. first `strict` and if `<clas 'UnicodeDecodeError'>`
	from old bash script with strange UTF codings then switch to `ignore` and read again
	"""
	lAllLines = []
	sErr = 'strict'
	while True:
		try:
			with open(sFile, mode = 'rt', encoding = 'utf-8', errors = sErr) as oPlik:
				for idx,sLine in enumerate(oPlik):
					sLine  = sLine[:-1]
					retVal = f_checkIfInclude(sLine)
					if retVal == -1: continue
					idx += 1 # add 1 because numering in KATE from 1 but in lists from 0
					lAllLines.append((idx,retVal,sLine))
				break # from while True:
		except Exception as err:
				if hasattr(err, 'message'): sError = err.message
				else: sError = err
				if str(type(err)) == "<class" + " 'UnicodeDecodeError'>":
					sErr = 'ignore'
				else:
					print(sError)
					quit()
	# ### end of while True:
	return lAllLines
def f_ChBtGroup(bChecked):              # sorting groups or line number
	global glMainListBoxLns
	if bChecked == True:
		# sorting on tuple(,,txt) from pos. `keyWord` from same tuple(,pos,)
		lArray = sorted(glMainListBoxLns, key = lambda x: x[2][x[1]:])
		glMainListBoxLns = f_fillListBox(lArray)
	else:
		if oqFilterInput.text() != '': # stil put filter on result after `grouping`
			f_liveEntry(oqFilterInput.text())
		else:
			lArray = sorted(glMatchLines)
			glMainListBoxLns = f_fillListBox(lArray)
	return None
def f_mainWinClose(*d):                   # finish
	if oApp.myExit:
		oApp.exit() # QT App quit
		quit() # Python quit
	if gsNOTES_HASH_CURRENT != hashlib.md5(oQnotesInMain.toPlainText().encode('utf-8')).hexdigest():
		glListOfConfigs[0]['notes'] = oQnotesInMain.toPlainText()
		qNotesDiffWin = QMessageBox(Qwindow)
		qNotesDiffWin.setFont(oQmainFont)
		qNotesDiffWin.setIcon(QMessageBox.Information)
		qNotesDiffWin.setText(f_Lng('mainWinQuitNotesInfo'))
		qNotesDiffWin.setWindowTitle(f_Lng('bigNotesInfoTtl'))
		qNotesDiffWin.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		qNotesDiffWin.setDefaultButton(QMessageBox.Yes)
		res = qNotesDiffWin.exec()
		if res == QMessageBox.Yes:
			with open(gsCONF_FILE, 'w', encoding = 'utf-8') as oFile:
				json.dump(glListOfConfigs, oFile, ensure_ascii = False)
	oApp.myExit = True
	Qwindow.close()
	return None
def f_checkRegWrdsAreOK(lWordsList):    # word for RegExp from given list are OK?
	global glCompRegWords
	lRegWords = []
	for elm in lWordsList:
		try:
			lRegWords.append(re.compile(elm))
		except re.error:
			return (False, elm) # Wrong word. Return this elm to open dialog win.
	glCompRegWords = list(lRegWords) # words for RegExp look ok so compiled list go to global
	return (True, "")
def f_getSize(*d):                      # monitor size of main win for pos. `ClearBtn` in `oqFilterInput`
	yPos = int((oqFilterInput.height() - oqBClear.height() ) /2)
	oqBClear.move(oqFilterInput.width() - oqBClear.width(), yPos) # set `clear btn` always at end
	return None
def f_about():                          # win with about
	xMainWin = Qwindow.pos().x()
	yMainWin = Qwindow.pos().y()
	sAuthor  = 'Radosław Głębicki'
	sEmail   = 'glebicki@o2.pl'
	sVersion = '1.x'
	with open(gsFILE, 'r', encoding='utf-8') as oFile: # skrypt read it self for data
		for idx,line in enumerate(oFile):
			if 'Author:' in line: sAuthor = line[:-1].split(': ')[1]
			if 'email:' in line: sEmail = line[:-1].split(': ')[1]
			if 'version:' in line: sVersion = line[:-1].split(': ')[1]
			if idx > 10: break

	sAboutTxt =  f_Lng('AboutAuthor')  + f": {sAuthor}\n"
	sAboutTxt += f_Lng('AboutEmail')   + f": {sEmail}\n"
	sAboutTxt += f_Lng('AboutVersion') + f": {sVersion}\n\n"
	sAboutTxt += f_Lng('AboutTxt')

	qMsgWin = QMessageBox()
	qMsgWin.setFont(oQmainFont)
	qMsgWin.move(xMainWin - 250, yMainWin + 50)
	qMsgWin.setIcon(QMessageBox.Information)
	qMsgWin.setText(sAboutTxt)
	qMsgWin.setWindowTitle(f_Lng('AboutWinTtl'))
	qMsgWin.setStandardButtons(QMessageBox.Ok)
	
	qMsgWin.exec()
	return None
def f_lookForStrInWidgets(sSearch):     # look for string in widgets.objectName
	"""Look in all objects in whole oApp, filtering word sSearch
	and return back dict as {key=name_from_`objectName`_without_`conf-`:['txt_in_widget',widget_itself]}
	"""
	dObj = {}
	for wdg in oApp.allWidgets():
		sWidgetName = wdg.objectName()
		if sSearch in sWidgetName:
			if isinstance(wdg, QComboBox): # for comboBox have to use currentText
				sText = wdg.currentText()
			elif isinstance(wdg, QPlainTextEdit): # for QPlainText with notes
				sText = wdg.toPlainText()
			else:
				sText = wdg.text()
			dObj[sWidgetName[5:]] = [sText,wdg]
	return dObj
def f_settingsWin():                    # settings with font size, language etc.
	def m_setWinClose(*d):
		if not QsetBtnSave.isEnabled():
			d[0].accept()
			oTimerF.start()
			return None
		oQexitConf = QMessageBox(QsetWin)
		oQexitConf.setFont(oQmainFont) # FONT
		oQexitConf.setIcon(QMessageBox.Warning)
		oQexitConf.setWindowTitle(f_Lng('ExitConfWinTtl'))
		oQexitConf.setText(f_Lng('ExitConfMsg'))

		oYesBtn = oQexitConf.addButton(f_Lng('Yes'), QMessageBox.YesRole)
		oNoBtn  = oQexitConf.addButton(f_Lng('No'), QMessageBox.NoRole)
		oQexitConf.setDefaultButton(oNoBtn)
		res = oQexitConf.exec()
		if res == 0:
			d[0].accept() # accepting closing event
			oTimerF.start() # start checkin file for monitoring
			return None
		d[0].ignore() # ignore closing event
		return None
	def m_settSave(*d):
		return None
	def m_valuesChanged(*d):
		if [QfntSizeCombo.currentText(),QlngCombo.currentText()] != lBeginSettValues:
			QsetBtnSave.setEnabled(True) # enable or not save btn
		else:
			QsetBtnSave.setEnabled(False) # enable or not save btn
		return None
	QsetWin = QDialog(Qwindow)
	QsetWin.myExit = False # neccessery to close window by btn QBtnCancel
	QsetWin.myTxtsInAllFields = "" # hold texts from all fields. To compare of change. Active save btn
	QsetWin.closeEvent = m_setWinClose # overwrited function closeEvent
	oQsetFont = oQmainFont
	QsetWin.setFont(oQsetFont)
	QsetWin.resize( 200, gnConfWinH)
	QsetWin.setWindowTitle("Settings")

	QVerLayout = QVBoxLayout()

	#                                                                 font size
	QsetHorFntSizeLay = QHBoxLayout()
	QfntSizeCombo = QComboBox()
	QfntSizeCombo.setStyleSheet("combobox-popup: 0;")
	QfntSizeCombo.setFont(oQsetFont)
	for nElm in range(gnFSfrom,gnFSto): # fill ComboBox with elements
		QfntSizeCombo.addItem(str(nElm))
	QfntSizeCombo.setCurrentIndex(int(gdAppConf['fs']) - gnFSfrom)
	QfntSizeCombo.currentIndexChanged.connect(m_valuesChanged)

	QsetHorFntSizeLay.addWidget(QLabel("Choose font size"), stretch = 1)
	QsetHorFntSizeLay.addWidget(QfntSizeCombo)
	#                                                                 language
	QsetHorlangLay = QHBoxLayout()
	QlngCombo = QComboBox()
	QlngCombo.setStyleSheet("combobox-popup: 0;")
	QlngCombo.setFont(oQsetFont)
	for sElm in f_Lng('lang', bLst = True): # fill ComboBox with elements
		QlngCombo.addItem(sElm)
	QlngCombo.currentIndexChanged.connect(m_valuesChanged)

	QsetHorlangLay.addWidget(QLabel("Choose language"), stretch = 1)
	QsetHorlangLay.addWidget(QlngCombo)
	#                                                                Save/Cancel btns
	QsetHorBtnLay = QHBoxLayout()
	QsetBtnSave = QPushButton(f_Lng('QBtnSave'))
	QsetBtnSave.clicked.connect(m_settSave)
	QsetBtnCancel = QPushButton(f_Lng('QBtnCancel'))
	QsetBtnCancel.clicked.connect(QsetWin.close)

	QsetHorBtnLay.addWidget(QsetBtnSave)
	QsetHorBtnLay.addWidget(QsetBtnCancel)

	QsetBtnSave.setEnabled(False) # enable or not save btn

	QVerLayout.addLayout(QsetHorFntSizeLay) # font size
	QVerLayout.addLayout(QsetHorlangLay)    # language
	QVerLayout.addLayout(QsetHorBtnLay)     # Buttons Save Cancel
	QsetWin.setLayout(QVerLayout)

	lBeginSettValues = [QfntSizeCombo.currentText(),QlngCombo.currentText()]

	QsetWin.exec()

	""" begin grid layout with small elements x,y,w,h,fntSize,lng
	QConfGridLay = QGridLayout()
	aGridObjs = []
	aGridObjs.append((QLabel('X'),0,0))
	aGridObjs.append((QLineEdit(),1,0))
	oGridX = aGridObjs[-1][0]
	oGridX.setObjectName('conf-x')
	aGridObjs.append((QLabel('Y'),0,1))
	aGridObjs.append((QLineEdit(),1,1))
	oGridY = aGridObjs[-1][0]
	oGridY.setObjectName('conf-y')
	aGridObjs.append((QLabel('W'),0,2))
	aGridObjs.append((QLineEdit(),1,2))
	oGridW = aGridObjs[-1][0]
	oGridW.setObjectName('conf-w')
	aGridObjs.append((QLabel('H'),0,3))
	aGridObjs.append((QLineEdit(),1,3))
	oGridH = aGridObjs[-1][0]
	oGridH.setObjectName('conf-h')
	aGridObjs.append((QLabel(''),0,4))
	aGridObjs.append((QPushButton(" "+f_Lng('takeBtn')),1,4))
	aGridObjs[-1][0].setToolTip(f_Lng('takeBtn_TT')) # ### f_Lng
	aGridObjs[-1][0].clicked.connect(m_takeMainWin)
	nWidth = QConfWordsBtn.fontMetrics().boundingRect(f_Lng('takeBtn')).width()+15
	aGridObjs[-1][0].setMaximumWidth(nWidth)
	aGridObjs.append((QLabel(f_Lng('fs_label')),0,5))
	aGridObjs.append((QLineEdit(),1,5))
	oGridF = aGridObjs[-1][0]
	oGridF.setObjectName('conf-fs')
	aGridObjs.append((QLabel(f_Lng('lng_lbl')),0,6))
	oGridLng = QComboBox()
	oGridLng.setStyleSheet(sStyleSheet)
	oGridLng.setObjectName('conf-lng')
	aGridObjs.append((oGridLng,1,6))
	for elm in f_Lng('lng', bLst = True):
		oGridLng.addItem(elm)
	oGridLng.setCurrentIndex(gnLng)

	oGridX.setText(str(xMainWin))
	oGridY.setText(str(yMainWin))
	oGridW.setText(str(wMainWin))
	oGridH.setText(str(hMainWin))
	# oGridF.setText(lLstOfConfs[0]['fs'])
	oGridLng.currentTextChanged.connect(m_textChanged)

	for elm in aGridObjs:
		if elm[0].metaObject().className() == "QLineEdit": # In grid only for QLineEdit set validator
			elm[0].setValidator(QIntValidator())
			elm[0].textChanged.connect(m_textChanged)
		QConfGridLay.addWidget(elm[0],elm[1],elm[2])

	QConfGridLay.addWidget(QLabel(''),0,5) # last column just to push to left
	""" # end grid layout

	""" Pos and size: not negative? Grid x,y,w,h,fs for saving
	sErrorL0 = f_Lng('lngErrorL0')
	if int(oGridX.text()) < 0:
		oGridX.setStyleSheet(sErrorColor + sConfFntSize)
		oGridX.setToolTip(sErrorL0)
		bSomethingWrong = True
	if int(oGridY.text()) < 0:
		oGridY.setStyleSheet(sErrorColor + sConfFntSize)
		oGridY.setToolTip(sErrorL0)
		bSomethingWrong = True
	if int(oGridW.text()) < 0:
		oGridW.setStyleSheet(sErrorColor + sConfFntSize)
		oGridW.setToolTip(sErrorL0)
		bSomethingWrong = True
	if int(oGridH.text()) < 0:
		oGridH.setStyleSheet(sErrorColor + sConfFntSize)
		oGridH.setToolTip(sErrorL0)
		bSomethingWrong = True
	# Field with font size
	if int(oGridF.text()) < 8 or int(oGridF.text()) > 14:
		oGridF.setStyleSheet(sErrorColor + sConfFntSize)
		bSomethingWrong = True
		if int(oGridF.text()) < 0: oGridF.setToolTip(f_Lng('lngFS_TT'))
		else: oGridF.setToolTip(f_Lng('lngFS_range'))
	""" # end checking small elements
	return None
def f_winChooseConf():                      # ### open window to choose current config
	global glListOfConfigs, glMatchLines, glMainListBoxLns, gsNOTES_HASH_CURRENT
	xMainWin = Qwindow.x()
	yMainWin = Qwindow.y()
	wMainWin = Qwindow.width()
	hMainWin = Qwindow.height()
	sErrorColor  = f"background: {gsColErr}; "
	sConfFntSize = f"font-size: {gdAppConf["fs"]}pt; " # FONT
	sStyleSheet = f"""	QComboBox {{ {sConfFntSize} }}
						QListView {{ border: 1px solid {gsColSel}; selection-background-color: {gsColSel} ;}}
						QScrollBar::add-line:vertical {{ border: none; background: none; }}
						QScrollBar::sub-line:vertical {{ border: none; background: none; }}""".replace("\t","")
	lLstOfConfs = [] # copy of glListOfConfigs for local manipulation
	for idx,elm in enumerate(glListOfConfigs): # moving data from global to local list
		dTmp = {}
		for key in glKeysOrder: # choosing only neccessey fields DEF:IUY875
			dTmp[key] = elm[key]
		lLstOfConfs.insert(idx,dTmp)
	dDictOfWdgs  = {} # dict of elms in conf win which hold data what are manipulated
	oTimerF.stop()

	def m_textChanged(*d):
		if QConfWin.myTxtsInAllFields == "".join([dDictOfWdgs[key]['method']() for key in  dDictOfWdgs.keys()]):
			for key in dDictOfWdgs.keys(): # each object with possibilty change text
				dDictOfWdgs[key]['wdg'].setStyleSheet(f"background-color: none; {sConfFntSize}") # set color back from "gsColErr"
		m_enableDisableSaveBtn()
		return None
	def m_enableDisableSaveBtn(bForce = None):
		if bForce is not None:
			QBtnSave.setEnabled(bForce)
			return None
		if QConfCombo.lineEdit().text() == "" or QConfWrdsInp.text() == "" or QConfFileInput.text() == "":
			QBtnSave.setEnabled(False)
		else:
			QBtnSave.setEnabled(True)
		return None
	def m_chooseFile(sFile = None, bChoice = True): # choosing file.py for monitoring
		""" sFile   - `path + file` to check for existance, lenght, nonbinary
			bChoice - default: choose from QFileDialog or go to check with given
		"""
		def m_setError(sF,sE):
			print(sE)
			QConfFileInput.setStyleSheet(sErrorColor + sConfFntSize)
			QConfFileInput.setToolTip(sE)
			QConfFileInput.setText(sF)
			return None

		sLocate = ""
		if gbDEBUG: sLocate = "m_chooseFile: "

		if bChoice:
			sFile = QFileDialog.getOpenFileName(QConfWin, f_Lng('m_chooseFile'), '/',"")[0] # tuple back so only [0]
		if sFile == "":
			sErr = f"{sLocate}There is no file to check!"
			m_setError(sFile,sErr)
			return -1 # no file to read
		else: # check if is text or binary
			if not os.path.isfile(sFile): # file doesn't exist'
				sErr = f"{sLocate}Given file doesn't exist!"
				m_setError(sFile,sErr)
				return -1
			else:
				if os.path.getsize(sFile) == 0:
					sErr = f"{sLocate}Given file is empty!"
					m_setError(sFile,sErr)
					return -1
				else: # sFile is not empty. file exists and size is bigger then 0 so now is text or binary
					try:
						with open(sFile, 'rb') as oFile:
							nPart = 1024
							binPart = oFile.read(nPart)
					except Exception as oErr:
						sErr = f"{sLocate}" + str(oErr)
						m_setError(sFile,sErr)
						return -1 # error
					if b'\x00' in binPart: # binary file
						sErr = f"{sLocate}Given file is binary!"
						m_setError(sFile,sErr)
						return -1 # error
		QConfFileInput.setStyleSheet(f"background-color: none; {sConfFntSize}")
		QConfFileInput.setToolTip(sFile)
		QConfFileInput.setText(sFile)
		return 0 # is OK
	def m_confSave(): # config save
		# BEGIN All fields to check in conf win
		bSomethingWrong = False
		# Conf name
		if QConfCombo.currentText() == '':
			QConfCombo.setStyleSheet(sErrorColor + sConfFntSize)
			QConfCombo.setToolTip('QConfCombo_ErrTT')
			bSomethingWrong = True
		# Field with file: exists?
		nRes = m_chooseFile(sFile = QConfFileInput.text(), bChoice = False)
		if nRes == -1: bSomethingWrong = True
		# Sentence field: regexp is ok?
		lArrToSave = f_strToList(QConfWrdsInp.text())
		tRes = f_checkRegWrdsAreOK(lArrToSave)
		if tRes[0] != True:
			sErrorTxt  = f_Lng('lng_sRes_Err1') + tRes[1]
			sErrorTxt += f_Lng('lng_sRes_Err2')
			QConfWrdsInp.setStyleSheet(sErrorColor + sConfFntSize)
			QConfWrdsInp.setFont(oQmainFont)
			QConfWrdsInp.setToolTip(sErrorTxt)
			if gbDEBUG: print(sErrorTxt)
			bSomethingWrong = True

		if bSomethingWrong: # Something is not ok: return
			return None
		# END

		# After checking words for Regexp (are ok) and rest of fields, continue to save of conf
		global glListOfConfigs, glMatchLines, glMainListBoxLns, gsNOTES_HASH_CURRENT
		dForJSON = {}
		dWdgWith_conf = f_lookForStrInWidgets('conf-')
		dForJSON['name'] = dWdgWith_conf['name'][0]
		dForJSON['comment'] = dWdgWith_conf['comment'][0]
		dForJSON['words'] = f_strToList(dWdgWith_conf['words'][0]) # if sKey = `words` then create list of words
		dForJSON['file'] = dWdgWith_conf['file'][0]
		dForJSON['notes'] = dWdgWith_conf['notes'][0]

		lLstOfConfs.insert(0,dForJSON)
		with open(gsCONF_FILE, 'w', encoding = 'utf-8') as oFile: # write conf
			json.dump(lLstOfConfs, oFile, ensure_ascii = False, indent = 2)
		QConfWin.myExit = True
		QConfWin.close()

		if lLstOfConfs[0]['notes'] == "": sTxt = ""
		else: sTxt = lLstOfConfs[0]['notes']
		oQnotesInMain.setPlainText(sTxt)
		QWhatFileLblNm.setText(lLstOfConfs[0]['name'])
		QWhatFileLblNm.setToolTip(lLstOfConfs[0]['file'])
		QWhatFileLblFl.setText('...' + lLstOfConfs[0]['file'][-25:])
		QWhatFileLblFl.setToolTip(lLstOfConfs[0]['file'])

		glListOfConfigs = list(lLstOfConfs)

		gsNOTES_HASH_CURRENT = hashlib.md5(oQnotesInMain.toPlainText().encode('utf-8')).hexdigest()

		oqFilterInput.setText('')
		# WORK HERE no Matching lines list is empty some info maybe as PlaceholderText or tooltip
		glMatchLines     = f_readFile(glListOfConfigs[0]['file'])
		glMainListBoxLns = f_fillListBox(glMatchLines)
		return None #                                          ### end of m_confSave
	def m_delCurrConf():
		oQdelConf = QMessageBox(QConfWin)
		oQdelConf.setFont(oQmainFont)
		oQdelConf.setIcon(QMessageBox.Warning)
		oQdelConf.setWindowTitle(f_Lng('delConfWinTtl'))
		oQdelConf.setText(f_Lng('delConfMsg'))
		oQdelConf.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		oQdelConf.setDefaultButton(QMessageBox.No)
		res = oQdelConf.exec()
		if res == QMessageBox.No:
			return None
		idx = QConfCombo.currentIndex()
		del lLstOfConfs[idx]
		QConfCombo.removeItem(idx)
		if QConfCombo.count() <= 1: # only one element in ComboBox
			mnuDelete.setEnabled(False)
		return None # end of m_delCurrConf
	def m_comboIndexChanged(): # if changed then: all fields changed if and if "" then prepare `NEW ITEM`
		nNewIndex = QConfCombo.currentIndex()
		if QConfCombo.itemText(QConfCombo.count() - 1) == "" and nNewIndex < QConfCombo.count() - 1:
			QConfCombo.removeItem(QConfCombo.count() - 1)
		if nNewIndex == len(lLstOfConfs): return None # no filling fields bec. no index in lLstOfConfs, so return
		dDictOfWdgs['words']['wdg'].setText(','.join(lLstOfConfs[nNewIndex]['words']))
		dDictOfWdgs['comment']['wdg'].setText(lLstOfConfs[nNewIndex]['comment'])
		dDictOfWdgs['file']['wdg'].setText(lLstOfConfs[nNewIndex]['file'])
		dDictOfWdgs['notes']['wdg'].setText(lLstOfConfs[nNewIndex]['notes'])
		dDictOfWdgs['notes']['wdg'].setCursorPosition(0) # to see txt from begin
		return None
	def m_testWords():
		tRes = f_checkRegWrdsAreOK(f_strToList(QConfWrdsInp.text()))
		if tRes[0] != True:
			QConfWrdsInp.setStyleSheet(f"{sErrorColor} {sConfFntSize}")
			sErrorTxt =  f_Lng('m_tWords_Err1') + f'<br><br><span style="background-color: {gsColErr};">{tRes[1]}</span><br><br>'
			sErrorTxt += f_Lng('m_tWords_Err2')
			print(f_Lng('m_tWords_Err1') + f'\n>>>{tRes[1]}<<<' + f_Lng('m_tWords_Err2'))
			f_Error(sErrorTxt, QConfWin)
		return None
	def m_isFileExists():
		if not os.path.isfile(QConfFileInput.text()):
			QConfFileInput.setStyleSheet(sErrorColor + sConfFntSize)
		return None
	def m_confWinClose(*d): # close this win and oTimerF (check file) is back on
		if not QBtnSave.isEnabled(): # btn Save is disabled means no changes made
			QConfWin.myExit = True # exiting
		if QConfWin.myExit:
			d[0].accept()
			oTimerF.start()
			return None
		oQexitConf = QMessageBox(QConfWin)
		oQexitConf.setFont(oQmainFont) # FONT
		oQexitConf.setIcon(QMessageBox.Warning)
		oQexitConf.setWindowTitle(f_Lng('ExitConfWinTtl'))
		oQexitConf.setText(f_Lng('ExitConfMsg'))

		oYesBtn = oQexitConf.addButton(f_Lng('Yes'), QMessageBox.YesRole)
		oNoBtn  = oQexitConf.addButton(f_Lng('No'), QMessageBox.NoRole)
		oQexitConf.setDefaultButton(oNoBtn)
		res = oQexitConf.exec()
		if res == 0:
			d[0].accept() # accepting closing event
			oTimerF.start() # start checkin file for monitoring
			return None
		d[0].ignore() # ignore closing event
		return None
	def m_addNewConf(*d):
		QConfCombo.addItem("")
		QConfCombo.setCurrentIndex(QConfCombo.count() - 1) # add new item at the end in comboBox
		QConfCombo.lineEdit().setPlaceholderText("Give some unique name")
		QConfCommInp.setText("")
		QConfCommInp.setPlaceholderText("Place some comment (not required)") # LANG
		QConfWrdsInp.setText("")
		QConfWrdsInp.setPlaceholderText(f_Lng('def_words'))
		QConfWrdsInp.setStyleSheet(f"background-color: none; {sConfFntSize}")
		QConfFileInput.setText("")
		QConfFileInput.setPlaceholderText("Choose file with src. code")
		QConfFileInput.setToolTip(f_Lng('lngFlToMon_TT'))
		QConfFileInput.setStyleSheet(f"background-color: none; {sConfFntSize}")
		QConfNotes.setText("")
		QConfNotes.setPlaceholderText("Edit `Notes` from Main Window")
		return None
	def m_configDuplicate():
		nCurrIdx = QConfCombo.currentIndex()
		lItemsInCombo = [QConfCombo.itemText(i) for i in range(QConfCombo.count())]
		sDupName = QConfCombo.currentText() + "_2"
		while True:
			if sDupName not in lItemsInCombo:
				break
			sDupName = sDupName + "_2"
		QConfCombo.insertItem(nCurrIdx,sDupName)
		lLstOfConfs.insert(nCurrIdx,lLstOfConfs[nCurrIdx])
		QConfCombo.setCurrentIndex(nCurrIdx)
		return None

	# ### Set configuration window
	QConfWin = QDialog(Qwindow) # WidgDef QConfWin
	QConfWin.myExit = False # neccessery to close window by btn QBtnCancel
	QConfWin.myTxtsInAllFields = "" # hold texts from all fields. To compare of change. Active save btn
	QConfWin.closeEvent = m_confWinClose # overwrited function closeEvent
	oQconfFont = oQmainFont
	QConfWin.setFont(oQconfFont)
	QConfWin.resize( gnConfWinW, gnConfWinH)
	QConfWin.setWindowTitle(f_Lng('QConfWinTtl'))
	# Vertical layout for whole window
	QVerLayout = QVBoxLayout()
	# Config choose - label
	QConfListLabel = QLabel(f_Lng('QConfLiLbl'))
	# ComboBox with input
	QConfCombo = QComboBox()
	# QConfCombo.text = QConfCombo.currentText # change method name ??????!!!!!!
	QConfCombo.setToolTip(f_Lng('QConfLiLbl_TT'))
	# QConfCombo -> connect must be at the end after oOrgElms creation:  -> GOTO:asdf567
	QConfCombo.setMaxVisibleItems(10)
	QConfCombo.setEditable(True)
	QConfCombo.lineEdit().setObjectName('conf-name')
	dDictOfWdgs['name'] = {'wdg':QConfCombo,'method':QConfCombo.lineEdit().text,} # hold widget and method to read text
	QConfCombo.setCompleter(None)
	QConfCombo.setStyleSheet(sStyleSheet)
	# QConfCombo.setObjectName('conf-name')
	for idx,elm in enumerate(lLstOfConfs): # fill ComboBox with elements
		QConfCombo.addItem(elm['name'])

	# BEGIN conf win menu creation
	oConfMenuWdg = QMenu()
	oConfMenuWdg.setStyleSheet(gsMenuStyleSheet)
	oConfMenuWdg.setTearOffEnabled(False)

	oConfMenu = oConfMenuWdg.addMenu("")
	oConfMenu.setToolTipsVisible(True)
	oConfMenu.setFont(oQmainFont)

	mnuNewConf = QAction("Create new config")
	mnuNewConf.triggered.connect(m_addNewConf)

	mnuDuplic = QAction("Duplicate config")
	mnuDuplic.triggered.connect(m_configDuplicate)

	mnuDelete = QAction("Delete config")
	mnuDelete.triggered.connect(m_delCurrConf)
	if QConfCombo.count() < 2: # only one element in ComboBox
		mnuDelete.setEnabled(False)

	oConfMenu.addAction(mnuNewConf)
	oConfMenu.addAction(mnuDuplic)
	oConfMenu.addAction(mnuDelete)

	# Menu button
	QConfComboOpt = QPushButton("opt")
	# QConfComboOpt.setIcon(QIcon.fromTheme('ibus-setup')) #'start-here'))
	QConfComboOpt.setFont(oQmainFont)
	# QConfComboOpt.setShortcut('Ctrl+m')
	QConfComboOpt.setFixedWidth(QConfComboOpt.fontMetrics().boundingRect("opt").width() +20)
	QConfComboOpt.setMenu(oConfMenu)
	# END conf win menu creation
	# Horizontal layout for QConfCombo and menu btn
	QConfHorLayout = QHBoxLayout()
	QConfHorLayout.addWidget(QConfCombo, stretch = 1)
	QConfHorLayout.addWidget(QConfComboOpt) # options btn menu for QConfCombo
	# Comment
	QConfCommLbl = QLabel(f_Lng('QCommLab'))
	#
	QConfCommInp = QLineEdit(lLstOfConfs[0]['comment'])
	dDictOfWdgs['comment'] =  {'wdg':QConfCommInp,'method':QConfCommInp.text,}
	QConfCommInp.setObjectName('conf-comment')
	QConfCommInp.textChanged.connect(m_textChanged)
	# words/sentences
	QConfWrdsLbl = QLabel(f_Lng('QConfWordsLbl'))
	# words input
	QConfWrdsInp = QLineEdit(','.join(lLstOfConfs[0]['words']))
	dDictOfWdgs['words'] =  {'wdg':QConfWrdsInp,'method':QConfWrdsInp.text,}
	QConfWrdsInp.setObjectName('conf-words')
	QConfWrdsInp.setToolTip(f_Lng('QConfWords_TT'))
	QConfWrdsInp.textChanged.connect(m_textChanged)
	QConfWrdsInp.editingFinished.connect(m_testWords)
	# test btn
	QConfWordsBtn = QPushButton(" &"+f_Lng('QConfWordsBtn')+' (?) ')
	QConfWordsBtn.setShortcut('Ctrl+t')
	nWidth = QConfWordsBtn.fontMetrics().boundingRect(" "+f_Lng('QConfWordsBtn')+' (?) ').width() + 20
	QConfWordsBtn.setFixedWidth(nWidth)
	QConfWordsBtn.setToolTip(f_Lng('QConfWordsBtn_TT'))
	# hor lay for words
	QConfHorWordsLayout = QHBoxLayout()
	QConfHorWordsLayout.addWidget(QConfWrdsInp)
	QConfHorWordsLayout.addWidget(QConfWordsBtn)
	# file
	QConfFileLabel = QLabel(f_Lng('QConfFileLbl'))
	# QConfFileInput is added to HorLayout and after horizontally button: choose file
	QConfFileInput = QLineEdit(lLstOfConfs[0]['file'])
	dDictOfWdgs['file'] =  {'wdg':QConfFileInput,'method':QConfFileInput.text,}
	QConfFileInput.setToolTip(lLstOfConfs[0]['file'])
	QConfFileInput.setObjectName('conf-file')
	QConfFileInput.textChanged.connect(m_textChanged)
	QConfFileInput.editingFinished.connect(m_isFileExists)
	# file btn
	QConfReadFileBtn = QPushButton(f_Lng('QConfReadFileBtn')+'(?) ')
	QConfReadFileBtn.setShortcut('Ctrl+f')
	QConfReadFileBtn.setToolTip('ctrl+f')
	nWidth = QConfReadFileBtn.fontMetrics().boundingRect(f_Lng('QConfReadFileBtn') + '(?) ').width() + 20
	QConfReadFileBtn.setMaximumWidth(nWidth)
	QConfReadFileBtn.clicked.connect(m_chooseFile)

	QConfHorFileLay = QHBoxLayout()
	QConfHorFileLay.addWidget(QConfFileInput) # to HorLayout adding fileInput
	QConfHorFileLay.addWidget(QConfReadFileBtn, stretch = 1) # to HorLayout adding QFileDialog
	# notes in setup window
	QConfNotes = QLineEdit()
	dDictOfWdgs['notes'] =  {'wdg':QConfNotes,'method':QConfNotes.text,}
	QConfNotes.setToolTip(f_Lng('confNotesEdit'))
	QConfNotes.setFont(oQconfFont)
	QConfNotes.setFixedWidth(gnConfWinW)
	QConfNotes.setText(lLstOfConfs[0]['notes'])
	QConfNotes.setCursorPosition(0)
	QConfNotes.setObjectName('conf-notes')
	QConfNotes.setReadOnly(True)

	oqLabPos = QLabel(f_Lng('posLbl'))
	oqLabPos.setToolTip(f_Lng('posLbl_TT'))
	# Save/Cancel btns
	QConfHorBtnLay = QHBoxLayout()
	QBtnSave = QPushButton(f_Lng('QBtnSave'))
	QBtnSave.clicked.connect(m_confSave)
	QBtnCancel = QPushButton(f_Lng('QBtnCancel'))
	QBtnCancel.clicked.connect(QConfWin.close)

	QConfHorBtnLay.addWidget(QBtnSave)
	QConfHorBtnLay.addWidget(QBtnCancel)

	QBtnSave.setEnabled(False) # enable or not save btn

	QVerLayout.addWidget(QConfListLabel)
	QVerLayout.addLayout(QConfHorLayout)
	QVerLayout.addWidget(QConfCommLbl)
	QVerLayout.addWidget(QConfCommInp)
	QVerLayout.addWidget(QConfWrdsLbl)
	QVerLayout.addLayout(QConfHorWordsLayout)
	QVerLayout.addWidget(QConfFileLabel)
	QVerLayout.addLayout(QConfHorFileLay)
	QVerLayout.addWidget(QLabel(f_Lng('Notes')))
	QVerLayout.addWidget(QConfNotes)
	QVerLayout.addLayout(QConfHorBtnLay) # Buttons Save Cancel

	QConfWin.setLayout(QVerLayout)

	# here `connect` after create and fill oOrgElms HERE:asdf567
	QConfCombo.currentIndexChanged.connect(m_comboIndexChanged)
	QConfCombo.currentTextChanged.connect(m_textChanged)

	# string with all fields init
	QConfWin.myTxtsInAllFields = "".join([dDictOfWdgs[key]['method']() for key in  dDictOfWdgs.keys()])

	QConfWin.exec()

	return None # end f_winChooseConf
def f_readConfig():                     # read config json
	global glListOfConfigs, gnLng, gsNOTES_HASH_CURRENT

	def m_checkConfWordsAsRegExp(lLstToCheck):
		global glListOfConfigs
		sNext = f_Lng('sNext1')
		while True:
			tRes = f_checkRegWrdsAreOK(lLstToCheck)
			if tRes[0] != True: # Wrong word/phrase for regexp
				sErrorTxt =  sNext + f_Lng('m_checkConfW_ErrTxt_1') + tRes[1]
				sErrorTxt += f_Lng('m_checkConfW_ErrTxt_2')
				print(sErrorTxt)
				f_Error(sErrorTxt,None)
				idx = glListOfConfigs[0]['words'].index(tRes[1])
				del glListOfConfigs[0]['words'][idx]
				sNext = f_Lng('sNext2')
			else: break
		return None # end m_checkWordsAsRegExp()

	try:
		if os.path.getsize(gsCONF_FILE) == 0: raise Exception('Config file lenght is 0!')
		with open(gsCONF_FILE, 'rt', encoding = 'utf-8') as oFile:
			glListOfConfigs = json.load(oFile)
			gsNOTES_HASH_CURRENT = hashlib.md5(glListOfConfigs[0]['notes'].encode('utf-8')).hexdigest()
	except Exception as err: # No conf file so it use own words
		if hasattr(err, 'message'): print(err.message)
		else: print(err)
		f_chooseLng()
		f_Error(f_Lng('f_readConfig_ErrTxt') + "\n" + f_Lng('f_readConfig_Error') + str(err),None)
		nScrHeight = oApp.primaryScreen().size().height()
		glListOfConfigs = [{'name':f_Lng('lngDefProgName'),'comment':f_Lng('lngDefComment'),
				'words':['NOTE ','BEGIN ','def [f_|m_]'],'file':gsFILE,
				'x':"0",'y':"0",'w':'200','h':nScrHeight,'fs':"12",'lng':str(gnLng), 'notes': ""},]
	m_checkConfWordsAsRegExp(glListOfConfigs[0]['words']) # checking default words and generating list glCompRegWords
	gnLng = 0 # LANG
	return None
def f_chooseLng():                      # choose the lang from list for f_Lng
	global gnLng
	def m_setLng(*d):
		global gnLng
		oPar4Item = d[0].listWidget()
		gnLng = oPar4Item.row(oPar4Item.currentItem())
		oAskLngWin.close()
		return None

	oAskLngWin = QWidget()
	oAskLngWin.resize(gnConfWinW,gnConfWinH)
	oScreen = oApp.primaryScreen().size()
	oAskLngWin.setWindowTitle('cdNav')

	QVerLngLay = QVBoxLayout()
	QVerLngLay.setContentsMargins(5,5,5,5)

	lLst = f_Lng('chooseLang',bLst = True) # get list of languages

	oQlngList = QListWidget(parent = oAskLngWin)
	oQlngList.setFont(oQmainFont)
	oQlngList.setStyleSheet(gsColSelInLst)
	oQlngList.addItems(lLst)
	oQlngList.itemClicked.connect(m_setLng)

	QVerLngLay.addWidget(oQlngList)
	oAskLngWin.setLayout(QVerLngLay)
	oAskLngWin.show()
	oApp.exec()

	if gnLng == None: # win was just closed
		oApp.quit()
		quit()
	return None
def f_fileToKate():                            # load choosen file to Kate
	sFile = glListOfConfigs[0]['file']
	if not os.path.isfile(sFile):
		print(f_Lng('QConfFileLbl') + "\n" + sFile + f_Lng('notExists'))
		f_Error(f_Lng('QConfFileLbl') + "\n" + sFile + f_Lng('notExists'))
		return None
	try:
		subprocess.Popen(f"kate {sFile}", shell = True)
	except Exception as sError:
		print(f_Lng('noKate') + str(sError))
		f_Error(f_Lng('noKate') + str(sError))
	return None
def f_clipNewData():                    # go to line number from clipboard (win have to be active)
	sClip = oClipboard.text()
	if sClip == "": return None
	if oClipboard.oldDataClipboard == sClip: return None # is that same so go back
	oClipboard.oldDataClipboard = sClip # remember if changed
	if sClip.isnumeric():
		oGoToBtn.setEnabled(True)
		oGoToBtn.setText(f_Lng('Gotoline') + sClip)
		return None
	if 'GOTO' in sClip: # maybe later add this
		oGoToBtn.setEnabled(True)
		oGoToBtn.setText(gsGO_TO_ANCHOR + 'ANC' + sClip[4:])
	return None
def f_GoToLine(oClickedBtn):           # go to line number in Kate
	if 'ANC' in oClickedBtn.text(): # anchor in text maybe later
		pass
	else:
		nColonPos = oClickedBtn.text().index(':')
		sLineNr = oClickedBtn.text()[nColonPos + 1:]
	os.system(f"kate -l {sLineNr}")
	return None
def f_editNotes(*d):                           # Open bigger edit fields
	"""Open bigger edit fields"""
	def m_EditWinClose(*d):
		quitNOTES_HASH_CURRENT = hashlib.md5(QbigText.toPlainText().encode('utf-8')).hexdigest()
		if quitNOTES_HASH_CURRENT != gsNOTES_HASH_CURRENT:
			qEditDiffWin = QMessageBox(QEditWin)
			qEditDiffWin.setFont(oQmainFont)
			qEditDiffWin.setIcon(QMessageBox.Information)
			qEditDiffWin.setText(f_Lng('bigNotesWasChanged'))
			qEditDiffWin.setWindowTitle(f_Lng('bigNotesInfoTtl'))
			qEditDiffWin.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
			qEditDiffWin.setDefaultButton(QMessageBox.Yes)

			res = qEditDiffWin.exec()
			if res == QMessageBox.Yes:
				oQnotesInMain.setPlainText(QbigText.toPlainText())
				glListOfConfigs[0]['notes'] = QbigText.toPlainText()

		QEditWin.close
		return None

	nEditWinWidth = 500
	nEditWinHeight = 400

	QEditWin = QDialog(Qwindow)
	QEditWin.setFont(oQmainFont)
	QEditWin.resize(nEditWinWidth, nEditWinHeight)
	QEditWin.setWindowTitle(f_Lng('notesEdit'))
	QEditWin.closeEvent = m_EditWinClose

	QbigText = QPlainTextEdit()
	if glListOfConfigs[0]['notes'] == "": QbigText.setPlaceholderText(f_Lng('bigerNotesBackgroundTxt'))
	else: QbigText.setPlainText(glListOfConfigs[0]['notes'])
	QVerBigTxtLay = QVBoxLayout()
	QVerBigTxtLay.addWidget(QbigText)

	QEditWin.setLayout(QVerBigTxtLay)
	QEditWin.exec()
	return None

oApp = QApplication(sys.argv)
oApp.myExit = False # for closing purpose
oApp.setStyle(QStyleFactory.create('Fusion'))
f_readConfig() # read configuration data if not conf will be set default val
glMatchLines = f_readFile(glListOfConfigs[0]['file'])
gsFILE_TIME = os.stat(glListOfConfigs[0]['file']).st_mtime

gdAppConf['h'] = oApp.primaryScreen().size().height()

QToolTip.setFont(oQmainFont)

oClipboard = oApp.clipboard()
oClipboard.oldDataClipboard = "" # to hold old clipboard
oClipboard.dataChanged.connect(f_clipNewData)

Qwindow = QWidget() # WidgDef Qwindow main window
Qwindow.closeEvent = f_mainWinClose # overwrited function closeEvent

Qwindow.resizeEvent = f_getSize # Change size for butonaClear in filter input
Qwindow.setMinimumWidth(200)
Qwindow.setMinimumHeight(400)
Qwindow.move(int(gdAppConf['x']),int(gdAppConf['y']))
Qwindow.resize(int(gdAppConf['w']),600) #int(gdAppConf['h']))
Qwindow.setWindowTitle('cN')

# BEGIN File name layout
QWhatFileLayout = QVBoxLayout()
QWhatFileLayout.setContentsMargins(5,5,5,5)
QWhatFileLblNm = QLabel(glListOfConfigs[0]['name'])
QWhatFileLblNm.setAlignment(Qt.AlignCenter)
QWhatFileLblNm.setToolTip(glListOfConfigs[0]['file'])
QWhatFileLblFl = QLabel('...' + glListOfConfigs[0]['file'][-25:])
QWhatFileLblFl.setAlignment(Qt.AlignCenter)
QWhatFileLblFl.setToolTip(glListOfConfigs[0]['file'])
QWhatFileLayout.addWidget(QWhatFileLblNm)
QWhatFileLayout.addWidget(QWhatFileLblFl)
# END
# BEGIN layout menu, group checkmark and exit btn
QMenuLayout = QHBoxLayout()
QMenuLayout.setContentsMargins(5,5,5,0)
QMenuLayout.setSpacing(5)
# create menu in main win
oqMenuWdg = QMenu()
oqMenuWdg.setStyleSheet(gsMenuStyleSheet)
oqMenuWdg.setTearOffEnabled(False)

oqMenu = oqMenuWdg.addMenu("")
oqMenu.setToolTipsVisible(True)
oqMenu.setFont(oQmainFont)

menuLoad = QAction(QIcon.fromTheme('text-x-generic'),f_Lng('Load2Kate'))
menuLoad.setShortcut('Ctrl+l')
menuLoad.setToolTip(f_Lng("Load2Kate_TT"))
menuLoad.triggered.connect(f_fileToKate)

menuFile = QAction(f_Lng('File2Mon_Menu'))
menuFile = QAction(QIcon.fromTheme('document-open'),f_Lng('File2Mon_Menu'))
menuFile.setShortcut('Ctrl+f')
menuFile.setToolTip("openObject_MenuTT")
menuFile.triggered.connect(f_winChooseConf)

menuConfig = QAction(QIcon.fromTheme('preferences-system'),f_Lng('Config'))
# menuConfig.setShortcut('Ctrl+c')
menuConfig.setToolTip("openConf_MenuTT")
menuConfig.triggered.connect(f_settingsWin)

menuAbout = QAction(QIcon.fromTheme('help-about'),f_Lng('About'))
menuAbout.setToolTip("Open About window.")
menuAbout.triggered.connect(f_about)

menuExit = QAction(QIcon.fromTheme('application-exit'),f_Lng('Quit'))
menuExit.setToolTip(f_Lng('Quit_TT'))
menuExit.setShortcut('Ctrl+q')
menuExit.triggered.connect(Qwindow.close)

oqMenu.addAction(menuLoad)
oqMenu.addAction(menuFile)
oqMenu.addSeparator()
oqMenu.addAction(menuAbout)
oqMenu.addSeparator()
oqMenu.addAction(menuConfig)
oqMenu.addSeparator()
oqMenu.addSeparator()
oqMenu.addAction(menuExit)
# """
# Menu button
oqMenuBtn = QPushButton(f_Lng('Menu'))
oqMenuBtn.setIcon(QIcon.fromTheme('ibus-setup')) #'start-here'))
oqMenuBtn.setFont(oQmainFontB)
oqMenuBtn.setShortcut('Ctrl+m')
oqMenuBtn.setMinimumWidth(oqMenuBtn.fontMetrics().boundingRect(f_Lng('Menu')).width())
oqMenuBtn.setMenu(oqMenu)
# END
# Group checkMark
oqChBxSort = QCheckBox('&' + f_Lng('Group'))
oqChBxSort.setShortcut('Ctrl+g')
oqChBxSort.setToolTip(f_Lng('oqChBxSort_TT'))
oqChBxSort.setFont(oQmainFont)
oqChBxSort.toggled.connect(f_ChBtGroup)
# exit btn
oQuitBtn = QPushButton()
# BEGIN `X` or QIcon in oQuitBtn
"""Why like this. I asume on another system will be no `window-close` so I read it fromTheme
	if can't be readed then `oIcon.isNull()` should be True but:
	sIconName = 'window-close2' no QIcon and isNull is False and name is just `window` ???
	sIconName = 'w2indow-close' noIcon and isNull is True so is ok but what with this case above ???
	Maybe my mistake or not understanding well
"""
sBtnTxt = ""
sIconName = 'window-close'
oIcon = QIcon.fromTheme(sIconName)
if oIcon.name() != sIconName: sBtnTxt = "X"
if oIcon.availableSizes() is None: sBtnTxt = "X"
if sBtnTxt == "": oQuitBtn.setIcon(oIcon) #'start-here'))
else: oQuitBtn.setText(sBtnTxt)
# END
oQuitBtn.setToolTip(f_Lng('Quit'))
oQuitBtn.clicked.connect(Qwindow.close)
oQuitBtn.setMaximumWidth(25)

QMenuLayout.addWidget(oqMenuBtn)
QMenuLayout.addWidget(oqChBxSort)
QMenuLayout.addWidget(oQuitBtn)
# layout for GoTo btn and Quit btn
QMainHrGoToLayout = QHBoxLayout()
QMainHrGoToLayout.setContentsMargins(5,5,5,0)
QMainHrGoToLayout.setSpacing(5)
# buttons in layout
oGoToBtn = QPushButton(f_Lng('Gotoline')[:-2])
oGoToBtn.setEnabled(False)
oGoToBtn.clicked.connect(lambda: f_GoToLine(oGoToBtn))

QMainHrGoToLayout.addWidget(oGoToBtn)

oqFrame = QFrame()
# Horizontall layout for Filter Input with Clear Button
QMainHrLayout = QHBoxLayout()
QMainHrLayout.setContentsMargins(0,5,0,0)
# Filter Input
oqFilterInput = QLineEdit()
oqFilterInput.setFont(oQfilterPHTfont)
oqFilterInput.setStyleSheet(f"background-color: {gsColBkg};")
oqFilterInput.setToolTip(f_Lng('TTfilter'))
oqFilterInput.setPlaceholderText("Put text here to filter list below")
oqFilterInput.textChanged.connect(f_liveEntry)
# Clear Button inside Filter Input
oqBClear = QPushButton('X')
oqBClear.setCursor(QCursor(Qt.ArrowCursor)) # arrow above `Clear btn` in filter field
oqBClear.setParent(oqFilterInput)
oqBClear.move(int(gdAppConf['w']) - nXbtn,nYbtn) # Always to `right`
oqBClear.resize(20,21)
oqBClear.clicked.connect(lambda: oqFilterInput.setText(''))
oqBClear.setStyleSheet(f"background: {gsColBkg}; border: 1px solid green;")

QMainHrLayout.addWidget(oqFilterInput)

oQlist = QListWidget()
oQlist.setFont(oQmainFont)
oQlist.setStyleSheet(gsColSelInLst)
oQlist.itemClicked.connect(f_lineSelect)
# Notes
oQnotesInMain = QPlainTextEdit()
oQnotesInMain.setReadOnly(True)
oQnotesInMain.setObjectName('mainWinNotes')
# if `notes` empty give some hint text
if glListOfConfigs[0]['notes'] == "": oQnotesInMain.setPlaceholderText(f_Lng('hereAboutCode'))
else: oQnotesInMain.setPlainText(glListOfConfigs[0]['notes'])
oQnotesInMain.setWordWrapMode(False)
oQnotesInMain.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred))

QVerListLayout = QVBoxLayout()
QVerListLayout.setContentsMargins(5,0,0,0)

QHorAboveNotes = QHBoxLayout()
QHorAboveNotes.setContentsMargins(5,5,5,5)
QbtnEdit = QPushButton(f_Lng('mainWinEdit'))
QbtnEdit.clicked.connect(f_editNotes)

QHorAboveNotes.addWidget(QLabel(f_Lng('belowNotes')))
QHorAboveNotes.addStretch()
QHorAboveNotes.addWidget(QbtnEdit)

QVerListLayout.addWidget(oQlist)
QVerListLayout.addLayout(QHorAboveNotes)
QVerListLayout.addWidget(oQnotesInMain)

glMainListBoxLns = f_fillListBox(glMatchLines)

oQGridLayout = QGridLayout() # element, row, column, rowSpan, columnSpan, alignment
oQGridLayout.setContentsMargins(0,5,0,0)
oQGridLayout.setSpacing(0)
oQGridLayout.addLayout(QMenuLayout,0,0,1,2)
oQGridLayout.addLayout(QWhatFileLayout,1,0,1,2,Qt.AlignCenter)
oQGridLayout.addLayout(QMainHrGoToLayout,2,0,1,2)
oQGridLayout.addLayout(QMainHrLayout,3,0,1,2)  # `span` on 2 columns, row 2
oQGridLayout.addLayout(QVerListLayout,4,0,1,2) # `span` on 2 columns, row 3

Qwindow.setLayout(oQGridLayout)

Qwindow.show()

oTimerF = QTimer() # timer to check file changes
oTimerF.setInterval(gnTIME_INTERVAL) # ms
oTimerF.timeout.connect(f_Interval)
oTimerF.start()

sys.exit(oApp.exec())
quit()
