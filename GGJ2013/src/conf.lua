function love.conf(t)
    t.title = "7th Sense"
    t.author = "GGJ13-Team-UHH"
    t.identity = "7thsense"
    t.version = "0.8.0" -- Löve version
    t.console = false
    t.release = false
    t.screen.width = 1000
    t.screen.height = 670
    t.screen.fullscreen = false
    t.screen.vsync = false
    t.screen.fsaa = 0

    t.modules.joystick = false
    t.modules.audio = true
    t.modules.keyboard = true
    t.modules.event = true
    t.modules.image = true
    t.modules.graphics = true
    t.modules.timer = true
    t.modules.mouse = true
    t.modules.sound = true
    t.modules.physics = true
end

