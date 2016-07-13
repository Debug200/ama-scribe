#AMA Scribe, by /u/Debug200

#To use, run "python main.py (thread id)" from command prompt. Then copy/paste the content of output.txt into a reddit comment. Please provide credit when doing so.
#Example: To summarize this thread: https://www.reddit.com/r/IAmA/comments/4rospz/iama_daily_fantasy_sports_expert_and_the/ , then run "python main.py 4rospz".
#You can also pass in alternate output file name as a second argument, like so: "python main.py 4rospz alt_output.txt"

import praw
import sys
import io

#Global "constants"
user_agent_string = 'windows:com.debug200.amascribe:0.1 (by /u/debug200)'
thing_limit = 10
thread_id = sys.argv[1]
output_file_name = 'output.txt'
if len(sys.argv) >= 3:
	output_file_name = sys.argv[2]

#Debugging function for examining the attributes of a given object. Used since PRAW documentation does not give this information
def dump(obj):
	for attr in dir(obj):
		print "obj.%s = %s" % (attr, getattr(obj, attr))
	
#Unicode Convert
def uc_conv(value):
	try:
		return value.encode("utf-8")
	except UnicodeDecodeError:
		return value
	else:
		# value was valid ASCII data
		pass

#Begin by pulling all comments from the given thread, and flattening the tree
reddit_obj = praw.Reddit(user_agent=user_agent_string)
ama_submission = reddit_obj.get_submission(submission_id=thread_id)
ama_submission.replace_more_comments(limit=16, threshold=10)
flat_comments = praw.helpers.flatten_tree(ama_submission.comments)
reply_list = []

#Build list of all replies, questions (parents of replies), and their links
for comment in flat_comments:
	if isinstance(comment, praw.objects.Comment) and comment.author == ama_submission.author:
		if comment.is_root: #account for comments from OP that are not replies
			parent_link = ''
			parent_text = '*Top level comment*'
		else:
			parent_link = comment.permalink[:-7] + comment.parent_id[3:10]
			parent_text = reddit_obj.get_submission(parent_link).comments[0].body
		reply_list.append((uc_conv(parent_text.replace('\n', ' ')), parent_link, uc_conv(comment.body.replace('\n', ' ')), comment.permalink + '?context=1'))
		#break #LIMITS TO ONE - DEBUG ONLY

#Write list to file, along with Reddit table markup
f = io.open(output_file_name,'w',encoding='utf-8')
f.write(u'Question|Response\n')
f.write(u':-|:-\n')
for tuple in reply_list:
	try:
		f.write(uc_conv(tuple[0]) + u'|[' + uc_conv(tuple[2]) + u'](' + uc_conv(tuple[3]) + u')\n')
	except UnicodeDecodeError:
		continue
f.close()