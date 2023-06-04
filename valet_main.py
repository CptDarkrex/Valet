import os

import flask_discord.models
from flask import Flask, redirect, url_for, render_template
from flask_discord import DiscordOAuth2Session, requires_authorization



app = Flask(__name__)

app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"    # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = some id
app.config["DISCORD_CLIENT_SECRET"] = "some secret"
app.config["DISCORD_BOT_TOKEN"] = "some token"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

discord = DiscordOAuth2Session(app)

HYPERLINK = '<a href="{}">{}</a>'


def welcome_user(user):
    dm_channel = discord.bot_request("/users/@me/channels", "POST", json={"recipient_id": user.id})
    return discord.bot_request(
        f"/channels/{dm_channel['id']}/messages", "POST", json={"content": "Thanks for authorizing the app!"}
    )


@app.route("/")
def index():
    if not discord.authorized:
        return f"""
        {HYPERLINK.format(url_for(".login"), "Login")} <br />
        {HYPERLINK.format(url_for(".login_with_data"), "Login with custom data")} <br />
        {HYPERLINK.format(url_for(".invite_bot"), "Invite Bot with permissions 8")} <br />
        {HYPERLINK.format(url_for(".invite_oauth"), "Authorize with oauth and bot invite")}
        """
    if discord.authorized:
        user = discord.fetch_user()
        guilds = discord.fetch_guilds()

        guild_names = {}
        guild_ids = []
        for g in guilds:
            if g.permissions.administrator:
                guild_ids.append(g)
                # guild_names[f"{g}"] = f"{g.id}"
                # print()

                # print(g)
                # print(g.permissions.administrator)
                # guild_names = guild_names.append(g)
        print(guild_ids)

        return render_template('index.html',
                               render_user_avatar=user.avatar_url,
                               render_user_name=user.name,
                               render_logout="logout",
                               render_guild=guild_ids
                               )
    # return f"""
    # {HYPERLINK.format(url_for(".me"), "@ME")}<br />
    # {HYPERLINK.format(url_for(".logout"), "Logout")}<br />
    # {HYPERLINK.format(url_for(".user_guilds"), "My Servers")}<br />
    # {HYPERLINK.format(url_for(".add_to_guild", guild_id=475549041741135881), "Add me to 475549041741135881.")}
    # """


@app.route("/login/")
def login():
    return discord.create_session()


@app.route("/login-data/")
def login_with_data():
    return discord.create_session(data=dict(redirect="/me/", coupon="15off", number=15, zero=0, status=False))


@app.route("/invite-bot/")
def invite_bot():
    return discord.create_session(scope=["bot"], permissions=8, guild_id=464488012328468480, disable_guild_select=True)


@app.route("/invite-oauth/")
def invite_oauth():
    return discord.create_session(scope=["bot", "identify"], permissions=8)


@app.route("/callback/")
def callback():
    data = discord.callback()
    redirect_to = data.get("redirect", "/")

    user = discord.fetch_user()
    welcome_user(user)

    return redirect(redirect_to)


@app.route("/me/")
def me():
    user = discord.fetch_user()
    return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body><img src='{user.avatar_url or user.default_avatar_url}' />
<p>Is avatar animated: {str(user.is_avatar_animated)}</p>
<a href={url_for("my_connections")}>Connections</a>
<br />
</body>
</html>

"""


@app.route("/me/guilds/<w_id>")
def user_guilds_web(w_id):
    if discord.authorized:
        guilds = discord.fetch_guilds()

        print(f"this is guild {w_id}")

        guild_ids = []
        current_guild = []

        for g in guilds:
            if g.permissions.administrator:
                guild_ids.append(g)
                # print(g.approximate_member_count)

        for g in guild_ids:
            if ( f"{w_id}" == f"{g.id}" ):
                # current_guild = g.id
                print(f"current guild is {g.approximate_member_count(g.id, with_counts=True)}")

        print(current_guild)
    return "<br />".join([f"[ADMIN] {g.name}" if g.permissions.administrator else g.name for g in guilds])


@app.route("/add_to/<int:guild_id>/")
def add_to_guild(guild_id):
    user = discord.fetch_user()
    return user.add_to_guild(guild_id)


@app.route("/me/connections/")
def my_connections():
    user = discord.fetch_user()
    connections = discord.fetch_connections()
    return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body>
{str([f"{connection.name} - {connection.type}" for connection in connections])}
</body>
</html>

"""


@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for(".index"))


@app.route("/secret/")
@requires_authorization
def secret():
    return os.urandom(16)


if __name__ == "__main__":
    app.run(debug=True)
