#Requires Autohotkey v2
;AutoGUI creator: Alguimist autohotkey.com/boards/viewtopic.php?f=64&t=89901
;AHKv2converter creator: github.com/mmikeww/AHK-v2-script-converter
;EasyAutoGUI-AHKv2 github.com/samfisherirl/Easy-Auto-GUI-for-AHK-v2

if A_LineFile = A_ScriptFullPath && !A_IsCompiled
{
	myGui := Constructor()
	myGui.Show("w400 h655")
}

Constructor()
{	
	myGui := Gui()
	buttons := [
		{ x: 16, y: 8 }, { x: 16, y: 56 }, { x: 16, y: 104 }, { x: 16, y: 152 },
		{ x: 16, y: 200 }, { x: 16, y: 248 }, { x: 16, y: 296 }, { x: 16, y: 344 },
		{ x: 16, y: 392 }, { x: 16, y: 440 }, { x: 16, y: 488 }, { x: 16, y: 536 },
		{ x: 16, y: 584 }, { x: 208, y: 8 }, { x: 208, y: 56 }, { x: 208, y: 104 },
		{ x: 208, y: 152 }, { x: 208, y: 200 }, { x: 208, y: 248 }, { x: 208, y: 296 },
		{ x: 208, y: 344 }, { x: 208, y: 392 }, { x: 208, y: 440 }, { x: 208, y: 488 },
		{ x: 208, y: 536 }, { x: 208, y: 584 }
	]
	buttonNames := [
		"Бот 1", "Бот 2", "Бот 3", "Бот 4", "Бот 5", "Бот 6", "Бот 7", "Бот 8",
		"Бот 9", "Бот 10", "Бот 11", "Бот 12", "Бот 13", "Бот 14", "Бот 15", "Бот 16",
		"Бот 17", "Бот 18", "Бот 19", "Бот 20", "Бот 21", "Бот 22", "Бот 23", "Бот 24",
		"Бот 25", "Бот 26"
	]
	for index, coords in buttons {
		button := myGui.Add("Button", "x" coords.x " y" coords.y " w141 h39", buttonNames[index])
		button.OnEvent("Click", OnEventHandler*)
	}
	SB := myGui.Add("StatusBar", , "Status Bar")
	myGui.OnEvent('Close', (*) => ExitApp())
	myGui.Title := "Window"
	
	return myGui
}

OnEventHandler(ctrl)
{
	ToolTip("Click! This is a sample action.`n"
	. "Active GUI element values include:`n"  
	. "Button => " ctrl.Text, 77, 277)
	SetTimer () => ToolTip(), -3000 ; tooltip timer
}