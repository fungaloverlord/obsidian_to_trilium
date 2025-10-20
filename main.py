from trilium_py.client import ETAPI

# Initialize the ETAPI client
server_url = 'http://localhost:8080'
token = '9NOzNsvFz2oH_p6uSvOqU/lMrVOtB7vaFhdqQSYLUs8TSijMw2U3Axto='
ea = ETAPI(server_url, token)
content = '''
<p>
	boop&nbsp;
	<a class="reference-link" href="#root/mQzvFE0H0rNJ">
		Something_else
	</a>
</p>
'''
note_data = {
    "parentNoteId": "mQzvFE0H0rNJ",  # Use 'root' or specify a valid parent note ID
    "title": "Hello World",
    "content": content,
    "type": "text"
}

response = ea.create_note(**note_data)

# Check if the note was created successfully
if response:
    print(f"✅ Note created: {response['note']['noteId']}")
else:
    print("❌ Failed to create note.")