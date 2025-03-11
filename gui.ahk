
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
	Button1 := myGui.Add("Button", "x16 y8 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y56 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y104 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y152 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y200 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y248 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y296 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y344 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y392 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y440 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y488 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y536 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x16 y584 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y8 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y344 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y392 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y488 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y296 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y440 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y536 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y104 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y248 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y200 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y152 w141 h39", "Бот 1")
	Button1 := myGui.Add("Button", "x208 y584 w141 h39", "Бот 1")
	SB := myGui.Add("StatusBar", , "Status Bar")
	Button1 := myGui.Add("Button", "x208 y56 w141 h39", "Бот 1")
	Button1.OnEvent("Click", OnEventHandler)
	myGui.OnEvent('Close', (*) => ExitApp())
	myGui.Title := "Window"
	
	OnEventHandler(*)
	{
		ToolTip("Click! This is a sample action.`n"
		. "Active GUI element values include:`n"  
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n" 
		. "Button1 => " Button1.Text "`n", 77, 277)
		SetTimer () => ToolTip(), -3000 ; tooltip timer
	}
	
	return myGui
}