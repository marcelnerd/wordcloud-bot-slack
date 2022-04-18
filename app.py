import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from wordcloud import WordCloud
import json

#app = App(token=os.environ["SLACK_BOT_TOKEN"])
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.command("/wordcloud")
def wordcloud(client, ack, command):
    ack("Creating wordcloud...")

    origin_c_id = command["channel_id"]
    result = client.conversations_list()["channels"]
    channel_ids = []
    for channel in result:
        if channel["is_group"] == False and channel["is_im"] == False:
            if(channel["is_member"] == False):
                client.conversations_join(channel=channel["id"])
            channel_ids.append(channel["id"])

    msg = ""
    for c_id in channel_ids:
        messages = client.conversations_history(channel=c_id)["messages"]
        for message in messages:
            msg += message["text"] + " "

    configJSON = json.loads(open("config.json", "r").read())
    width = configJSON['resolution']['width']
    height = configJSON['resolution']['height']

    wordcloud = WordCloud(background_color=configJSON["wordcloud"]["background"],
        width=width - 2 * int(configJSON["wordcloud"]["margin"]),
        height=height - 2 * int(configJSON["wordcloud"]["margin"])).generate(msg)

    wordcloud.to_file("wordcloud.png")
    result = client.files_upload(
        channels=origin_c_id,
        initial_comment="Here is your daily wordcloud",
        file="./wordcloud.png",
    )

@app.event("app_mention")
def event_test(say):
    say("Hi there!")

# if __name__ == "__main__":
#     SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))