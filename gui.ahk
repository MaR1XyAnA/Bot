Gui, Add, Text,, Управление ботами

Loop, 3
{
    if (A_Index != 2) {
        Gui, Add, Text,, ; Пустая строка для выравнивания
    } else {
        Gui, Add, Text,, Бот %A_Index%
    }
    Gui, Add, Button, x10 y+30 gToggleBot%A_Index% vButton%A_Index%, бота %A_Index%
    Gui, Add, Text, x+5 yp vBotStatus%A_Index% cRed, ● ; Индикатор лампочка (красная - выключен)
}

Gui, Add, Button, x10 y+30 gCheckForUpdates, Проверить обновления ; Кнопка для ручной проверки обновлений

Gui, Show, w400 h300, Бот GUI ; Увеличенный размер окна

GuiControlGet, Button1Pos, Pos, Button1
GuiControlGet, Button2Pos, Pos, Button2
GuiControlGet, Button3Pos, Pos, Button3

GuiControlGet, BotStatus1Pos, Pos, BotStatus1
GuiControlGet, BotStatus2Pos, Pos, BotStatus2
GuiControlGet, BotStatus3Pos, Pos, BotStatus3

; Пример изменения координат
GuiControl, Move, Button1, x50 y50
GuiControl, Move, BotStatus1, x150 y50
GuiControl, Move, Button2, x50 y100
GuiControl, Move, BotStatus2, x150 y100
GuiControl, Move, Button3, x50 y150
GuiControl, Move, BotStatus3, x150 y150

; Автообновление с GitHub
SetTimer, CheckForUpdates, 3600000 ; Проверка обновлений каждый час

CheckForUpdates:
    RunWait, git fetch origin, , Hide
    RunWait, git reset --hard origin/main, , Hide
    Reload
return

ToggleBot1:
    if (Bot1Status := !Bot1Status) {
        ; Логика для включения бота 1
        GuiControl,, BotStatus1, ● ; Индикатор лампочка (зелёная - включен)
        GuiControl, +cGreen, BotStatus1
    } else {
        ; Логика для выключения бота 1
        GuiControl,, BotStatus1, ● ; Индикатор лампочка (красная - выключен)
        GuiControl, +cRed, BotStatus1
    }
return

ToggleBot2:
    if (Bot2Status := !Bot2Status) {
        ; Логика для включения бота 2
        GuiControl,, BotStatus2, ● ; Индикатор лампочка (зелёная - включен)
        GuiControl, +cGreen, BotStatus2
    } else {
        ; Логика для выключения бота 2
        GuiControl,, BotStatus2, ● ; Индикатор лампочка (красная - выключен)
        GuiControl, +cRed, BotStatus2
    }
return

ToggleBot3:
    if (Bot3Status := !Bot3Status) {
        ; Логика для включения бота 3
        GuiControl,, BotStatus3, ● ; Индикатор лампочка (зелёная - включен)
        GuiControl, +cGreen, BotStatus3
    } else {
        ; Логика для выключения бота 3
        GuiControl,, BotStatus3, ● ; Индикатор лампочка (красная - выключен)
        GuiControl, +cRed, BotStatus3
    }
return

GuiClose:
    ExitApp
