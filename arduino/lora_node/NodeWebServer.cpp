#include <Arduino.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <ESPAsyncWebServer.h>
#include "User.h"
#include "NodeWebServer.h"
#include "version.h"
#include "LoraNode.h"

// ====== Config ======
#define DNS_PORT 53
IPAddress apIP(192, 168, 4, 1);
String AP_SSID = "GAME_ON";
String AP_PASS = "";

/*#define MAX_MSGS 20
struct NodeMessage {
    String id;
    String user;
    String text;
    int ttl;
};

NodeMessage messages[MAX_MSGS];
int msgWriteIndex = 0;
*/
// ====== Webserver & DNS ======
AsyncWebServer NodeWebServer::httpServer(80);
DNSServer NodeWebServer::dnsServer;

// ====== Helpers ======
String escapeHtml(const String &input)
{
    String out = input;
    out.replace("&", "&amp;");
    out.replace("<", "&lt;");
    out.replace(">", "&gt;");
    out.replace("\"", "&quot;");
    out.replace("'", "&#39;");
    return out;
}

String getSessionToken(AsyncWebServerRequest *request)
{
    String session = "";
    Serial.println("[INFO] getSessionToken");
    if (request->hasHeader("Cookie"))
    {
        String cookies = request->getHeader("Cookie")->value();
        Serial.println("[INFO] Cookies: " + cookies);

        if (cookies.indexOf("session=") >= 0)
        {
            int start = cookies.indexOf("session=") + 8;
            int end = cookies.indexOf(";", start);
            if (end == -1)
                end = cookies.length();
            session = cookies.substring(start, end);
        }
    }

    Serial.println("[INFO] Session token: " + session);
    if ((session == "") && (request->hasArg("token")))
    {
        Serial.println("[INFO] Found token in request: " + request->arg("token"));

        session = request->arg("token");
    }

    Serial.println("[INFO] Session token: " + session);
    if ((session != "") && (!User::isValidToken(session)))
    {
        Serial.println("[INFO] invalid token: " + session);
        return "";
    }
    Serial.println("[INFO] Session token: " + session);

    return session;
}

const char PAGE_INDEX[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <style>
    body { font-family: Arial; margin: 20px; }
    input[type=text], input[type=password] { width: 80%; padding: 8px; }
    input[type=submit] { padding: 8px 16px; }
    div.box { margin-top:20px; padding:10px; border:1px solid #333; border-radius:8px; }
  </style>
</head>
<body>
  <h2>%TITLE% %USERNAME% %TEAM%</h2>

  <form action='/msg' method='POST'>
    <input type='text' name='msg' placeholder='Typ bericht...'>
    <input type='hidden' name='token' value='%TOKEN%'>
    <input type='submit' value='Verzend'>
  </form>

  <br><br>
  %ONLINE_NODES%

</body>
</html>
)rawliteral";

String NodeWebServer::makePage(String session)
{
    String page(PAGE_INDEX);
    String username = User::getNameBySession(session);
    String team = User::getUserTeamBySession(session);
    String title = "Game on Webserver " + RELEASE_ID;
    // Links
    String links = "<div class='box'><h3>Webserver Links</h3><ul>";
    links += "<li><a href='/'>Home</a></li>";
    links += "<li><a href='/register.html'>Register</a></li>";
    links += "<li><a href='/debug.html'>Debug</a></li>";
    links += "<li><a href='/msg'>Send Message (POST)</a></li>";
    links += "<li><a href='/generate_204.html'>Captive Portal</a></li>";
    links += "<li><a href='/fwlink.html'>FWLink</a></li>";
    links += "<li><a href='/hotspot-detect.html'>Hotspot Detect</a></li>";
    if (session.length() > 0)
    {
        links += "<li><a href='/logout'>Logout</a></li>";
    }
    else
    {
        links += "<li><a href='/login.html'>Login</a></li>";
    }
    links += "</ul></div>";
    // Online nodes lijst
    String nodeList = "<h3>Online Nodes</h3><ul>";
    int onlineCount = LoraNode::getOnlineCount();
    const OnlineNode *onlineNodes = LoraNode::getOnlineNodes();
    Serial.println("[INFO] Online nodes:" + String(onlineCount));
    nodeList += "<li>Online nodes: " + String(onlineCount) + "</li>";
    for (int i = 0; i < onlineCount; i++)
    {
        unsigned long now = millis();
        unsigned long lastSeen = onlineNodes[i].lastSeen;
        unsigned long secondsAgo = (now > lastSeen) ? (now - lastSeen) / 1000 : 0;
        nodeList += "<li>" + escapeHtml(onlineNodes[i].name) + " (RSSI: " + String(onlineNodes[i].rssi) + " dBm, SNR: " + String(onlineNodes[i].snr) + " dB, last seen: " + String(secondsAgo) + "s ago)</li>";
    }
    nodeList += "</ul>";
    // Gebruikerslijst toevoegen
    String userList = "<h3>Alle gebruikers</h3><ul>";
    int userCount = User::getUserCount();
    for (int i = 0; i < userCount; i++)
    {
        userList += "<li>" + escapeHtml(User::getUserName(i)) + " (" + User::getUserTeam(i) + ")</li>";
    }
    userList += "</ul>";
    // IP en token injecteren
    IPAddress ip = WiFi.softAPIP();
    String ipStr = ip.toString();
    page.replace("%AP_IP%", ipStr);
    // Voeg hidden field met token toe

    page.replace("%USERNAME%", username);
    page.replace("%TEAM%", team);
    page.replace("%TITLE%", title);
    
    // Zoek formulier en voeg hidden token toe
    page.replace("<input type='submit' value='Verzend'>", "<input type='submit' value='Verzend'>");
    page.replace("%ONLINE_NODES%", links + nodeList + userList);
    return page;
}

// ====== Routes ======
void NodeWebServer::setupRoot()
{
    httpServer.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
                  {
        Serial.println("[INFO] getSessionToken 2");    
        String session = getSessionToken(request);
        Serial.println("[INFO] Session token: " + session);
        if (session == "" ) {
            request->send(200, "text/html", "<h2>Welkom</h2><a href='/login.html'>Login</a>");
        } else {
            Serial.println("[INFO] Session token: " + session);
            String page = makePage(session);
            AsyncWebServerResponse *response = request->beginResponse(200, "text/html; charset=UTF-8", page);
            response->addHeader("Set-Cookie", "session=" + session + "; Path=/; Max-Age=86400");
            request->send(response);
        }
        return; });
}
void NodeWebServer::setupCaptivePortal()
{
    String page = "<html><head><meta http-equiv='refresh' content='10; url=http://192.168.4.1/index.html'></head><body>"
                  "<h3>Als je niet automatisch doorgestuurd wordt, klik <a href='http://192.168.4.1/index.html'>hier</a>.</h3>"
                  "<p>Voor volledige toegang: "
                  "<a href='http://192.168.4.1/' target='_blank'>Open in Safari</a></p>"
                  "</body></html>";

    // Captive portal common URLs
    httpServer.on("/generate_204.html", HTTP_GET, [page](AsyncWebServerRequest *request)
                  { request->send(204); });
    httpServer.on("/generate_204", HTTP_GET, [page](AsyncWebServerRequest *request)
                  { request->send(204); });
    httpServer.on("/fwlink.html", HTTP_GET, [page](AsyncWebServerRequest *request)
                  { request->send(204); });
    httpServer.on("/hotspot-detect.html", HTTP_GET, [](AsyncWebServerRequest *request)
                  { request->send(204); });
    httpServer.onNotFound([](AsyncWebServerRequest *request)
                          {
    // gewoon een 404 of simpele pagina sturen
    request->send(404, "text/plain", "Page not found. Open http://192.168.4.1 in Safari."); });
}

void NodeWebServer::setupLogin()
{
    httpServer.on("/login.html", HTTP_GET, [](AsyncWebServerRequest *request)
                  { request->send(200, "text/html",
                                  "<form method='POST' action='/login'>"
                                  "User:<input name='user'><br>"
                                  "Pass:<input type='password' name='pass'><br>"
                                  "Team:<input name='team'><br>"
                                  "<input type='submit'></form>"); });

    httpServer.on("/login", HTTP_POST, [](AsyncWebServerRequest *request)
                  {
        String user, pass;
        if (request->hasArg("user")) user = request->arg("user");
        if (request->hasArg("pass")) pass = request->arg("pass");

        if (User::isValidLogin(user, pass)) {
            String session = User::createSession(user);
            AsyncWebServerResponse *response = request->beginResponse(303);
            response->addHeader("Set-Cookie", "session=" + session + "; Path=/; Max-Age=86400");
            response->addHeader("Location", "/");
            request->send(response);
        } else {
            request->send(403, "text/html", "<p>Login mislukt</p>");
        } });
}

void NodeWebServer::setupRegister()
{
    httpServer.on("/register.html", HTTP_GET, [](AsyncWebServerRequest *request)
                  { request->send(200, "text/html",
                                  "<form method='POST' action='/register'>"
                                  "User:<input name='user'><br>"
                                  "Pass:<input type='password' name='pass'><br>"
                                  "Team:<input name='team'><br>"
                                  "<input type='submit'></form>"); });

    httpServer.on("/register", HTTP_POST, [](AsyncWebServerRequest *request)
                  {
        String user, pass, team;
        if (request->hasArg("user")) user = request->arg("user");
        if (request->hasArg("pass")) pass = request->arg("pass");
        if (request->hasArg("team")) team = request->arg("team");

        if (User::registerUser(user, pass, team)) {
            String session = User::createSession(user);
            AsyncWebServerResponse *response = request->beginResponse(303);
            response->addHeader("Set-Cookie", "session=" + session + "; Path=/; Max-Age=86400");
            response->addHeader("Location", "/");
            request->send(response);
        } else {
            request->send(400, "text/html", "<p>Gebruiker bestaat al</p>");
        } });
}

void NodeWebServer::setupLogout()
{
    httpServer.on("/logout", HTTP_GET, [](AsyncWebServerRequest *request)
                  {
        AsyncWebServerResponse *response = request->beginResponse(303);
        response->addHeader("Set-Cookie", "session=; Max-Age=0");
        response->addHeader("Location", "/");
        request->send(response); });
}

void NodeWebServer::setupDebug()
{
    httpServer.on("/debug.html", HTTP_GET, [](AsyncWebServerRequest *request)
                  {
        String page = "<h2>Debug info</h2>";
        page += "<p>Aantal berichten: " + String(MAX_MSGS) + "</p>";
        request->send(200, "text/html", page); });
}

void NodeWebServer::setupMessages()
{
    // GET: toon berichten
    httpServer.on("/msg", HTTP_GET, [](AsyncWebServerRequest *request)
                  {
        String token;

        Serial.println("[INFO] getSessionToken 3");
    
        String session = getSessionToken(request);
        if (session == "" ) {
            request->send(403, "text/html", "<p>Ongeldig of ontbrekend token.</p>");
            return;
        }

        String content = "<h2>Berichten</h2>";
        content += "<form method='POST' action='/msg'>";
        content += "Bericht: <input type='text' name='msg'><br>";
        content += "<input type='submit' value='Stuur'></form><br>";

        NodeMessage msg;
        for (int i = 0; i < LoraNode::getMsgCount(); i++) {
            msg = LoraNode::getMessage(i);
            content += "<b>" + escapeHtml(msg.user) + ":</b> "
                       + escapeHtml(msg.object) + " "
                       + escapeHtml(msg.function) + " "
                       + escapeHtml(msg.parameters) +  "<br>";
        }

        request->send(200, "text/html", content); });

    // POST: voeg bericht toe
    httpServer.on("/msg", HTTP_POST, [](AsyncWebServerRequest *request)
                  {
        String msg, user;
        Serial.println("[INFO] getSessionToken 4");
    
        String session = getSessionToken(request);
        if (session == "") {
            request->send(403, "text/html", "<p>Ongeldig of ontbrekend token.</p>");
            return;
        }
        if (request->hasArg("msg")) msg = request->arg("msg");

        user = User::getNameBySession(session);

        NodeMessage nodeMessage;
        nodeMessage.msgId = String(millis());
        nodeMessage.user = user;
        nodeMessage.TTL = 3;
        nodeMessage.timestamp = millis();
        nodeMessage.object = "MSG";
        nodeMessage.function = "SEND";
        nodeMessage.parameters = msg;

        LoraNode::addMessage(nodeMessage);

        AsyncWebServerResponse *response = request->beginResponse(303);
        response->addHeader("Location", "/msg");
        request->send(response); });
}

// ====== Init ======
void NodeWebServer::webserverSetup()
{
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
    WiFi.softAP(AP_SSID.c_str(), AP_PASS.c_str());

    setupRoot();
    setupCaptivePortal();
    setupLogin();
    setupRegister();
    setupLogout();
    setupDebug();
    setupMessages();

    httpServer.begin();
    dnsServer.start(DNS_PORT, "*", apIP);

    Serial.println("[INFO] Async Webserver gestart");
}

void NodeWebServer::webserverLoop()
{
    dnsServer.processNextRequest();
}
