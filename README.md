# SmartFeed #

**SmartFeeds** is an innovative Python tool that filters out noise from the vast amount of daily social media posts, 
helping users save time. It uses OpenAI algorithms to analyze and identify the most discussed social media narratives, 
providing a concise summary that highlights key ideas and topics of interest.

In its default and first version, SmartFeeds follows the main traders and storytellers in the cryptocurrency space on Twitter. 
However, this can be customized to follow any topic and social media platform.”

The application will provide a daily summary of the stories that have received the most attention on a 
social platform and send it to a Telegram channel.

The idea was initially established with the intention of utilizing technology to enhance the social media experience,
rather of wasting countless hours reading every message in an **dopamine infinitive feed**. 
Tools like "**SmartFeeds**" will become more and more crucial for people and organizations trying to keep current 
with the latest trends and advances without being a slave to another algorithm as the use of social media continues 
to expand and improve.

## Installation ##
You can install the Tweet Summarizer library by cloning the repository from GitHub:

### Clone the repository ###
```bash 
   git clone https://github.com/username/SmartFeeds.git
```
### Install the dependencies ###
```bash 
pip install -r requirements.txt
```
### Set your keys in the config.ini file ###
1) Twitter API keys:
You can get them from the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).
2) OpenAI API key:
   You can get it from the [OpenAI Developer Portal](https://beta.openai.com/).
3) Telegram API key:.
   You can get it from the [Telegram Developer Portal](https://core.telegram.org/bots/api).
4) Telegram channelId:
   * Create a group in Telegram or use an existing one.
   * Add the bot to the group.
   * Get the channel id, going to https://web.telegram.org/ and clicking on the group.
    * The channel id is the number in the url, https://web.telegram.org/z/#channelid
     
5) Youtube Api Key:
   * to the Google Cloud Console: You can access it at this link.

   * Create a new project: Click on the "Select a project" dropdown at the top of the page, and then click on "New Project." Give your project a name, then click "Create."

   * Enable the YouTube Data API v3: On your project dashboard, click on "Explore and enable APIs." In the API library, search for "YouTube Data API v3" and click on it. Then click on "Enable."

   * Create credentials: After the API is enabled, you'll be taken to a page where you can create credentials. Click on "Create Credentials" at the top of the page. In the form that appears, for "Which API are you using?" select "YouTube Data API v3." For "Where will you be calling the API from?" select the appropriate option, such as "Web server (e.g., node.js, Tomcat)." For "What data will you be accessing?" select "Public data." Then click "What credentials do I need?"

   * Create an API Key: You'll be taken to a page where you can create your API key. Give your key a name, and click "Create."

   * Secure your API Key: To prevent unauthorized use of your API key, you should restrict it to your server IP address or your website URL. To do this, click on the pencil icon next to your API key in the list of credentials, then under "Key restrictions" select "IP addresses" or "HTTP referrers" and enter your IP address or URL.

## Contributing ##
If you would like to contribute to the Tweet Summarizer library,
please create a new branch and submit a pull request with your changes.

## License ##
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
