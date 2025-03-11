local http = require("socket.http")
local ltn12 = require("ltn12")

local currentVersion = "1.0.0"
local repoUrl = "https://raw.githubusercontent.com/MaR1XyAnA/Bot/main/Bot_menu.lua"
local versionUrl = "https://raw.githubusercontent.com/MaR1XyAnA/Bot/main/version.txt"

local menu = {
    { name = "Очистить чат", action = function() --[[ Очистить чат ]] end },
    { name = "UnFreeze", action = function() --[[ UnFreeze ]] end },
    { name = "Скрыть диалог", action = function() --[[ Скрыть диалог ]] end },
    { name = "Выгрузить скрипт", action = function() --[[ Выгрузить скрипт ]] end },
    { name = "Подключиться", action = function() --[[ Подключиться ]] end },
    { name = "Телепорт метка", action = function() --[[ Телепорт метка ]] end },
    { name = "Показать диалог", action = function() --[[ Показать диалог ]] end },
    { name = "Перезагрузить скрипт", action = function() --[[ Перезагрузить скрипт ]] end },
    { name = "Отключиться", action = function() --[[ Отключиться ]] end },
    { name = "Телепорт чекпоинт", action = function() --[[ Телепорт чекпоинт ]] end },
    { name = "Починить колеса", action = function() --[[ Починить колеса ]] end },
    { name = "Сбросить настройки", action = function() --[[ Сбросить настройки ]] end },
    { name = "Закрыть соединение", action = function() --[[ Закрыть соединение ]] end },
    { name = "Умереть", action = function() --[[ Умереть ]] end },
    { name = "Отремонтировать авто", action = function() --[[ Отремонтировать авто ]] end },
    { name = "Удалить Скрипт", action = function() --[[ Удалить Скрипт ]] end },
    { name = "Slap Up", action = function() --[[ Slap Up ]] end },
    { name = "Slap Down", action = function() --[[ Slap Down ]] end },
    { name = "Заспавнить себя", action = function() --[[ Заспавнить себя ]] end },
    { name = "Обновить скрипт", action = function() updateScript() end },
}

function showMenu()
    for i, item in ipairs(menu) do
        print(string.format("%d. %s", i, item.name))
    end
    print("Выберите опцию:")
    local choice = tonumber(io.read())
    if choice and menu[choice] then
        menu[choice].action()
    else
        print("Неверный выбор")
    end
end

showMenu()

function openMenuCommand()
    showMenu()
end

-- Пример использования команды
-- openMenuCommand()

-- Обработка команды /ffr
function onCommandReceived(command)
    if command == "/ffr" then
        openMenuCommand()
    end
end

-- Пример вызова функции при получении команды
onCommandReceived("/ffr")

function checkForUpdates()
    local response = {}
    local _, code = http.request{
        url = versionUrl,
        sink = ltn12.sink.table(response)
    }
    if code == 200 then
        local latestVersion = table.concat(response)
        if latestVersion > currentVersion then
            print("Доступна новая версия: " .. latestVersion)
            print("Введите /update для обновления")
        else
            print("У вас установлена последняя версия")
        end
    else
        print("Не удалось проверить обновления")
    end
end

function updateScript()
    local response = {}
    local _, code = http.request{
        url = repoUrl,
        sink = ltn12.sink.table(response)
    }
    if code == 200 then
        local file = io.open("Bot_menu.lua", "w")
        file:write(table.concat(response))
        file:close()
        print("Скрипт обновлен, перезапуск...")
        -- Перезапуск скрипта
        os.execute("lua Bot_menu.lua")
        os.exit()
    else
        print("Не удалось обновить скрипт")
    end
end

-- Проверка обновлений при запуске
checkForUpdates()
