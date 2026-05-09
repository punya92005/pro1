def chatbot_reply(text):
    text = text.lower()

    if any(word in text for word in ["hi", "hello", "hey"]):
        return "Hello 👋 Welcome to BlogVerse!"

    elif "create" in text or "post" in text:
        return "👉 Click 'Create Post' to add a post."

    elif "like" in text:
        return "❤️ Click Like button below the post."

    elif "comment" in text or "reply" in text:
        return "💬 Use comment box under the post."

    elif "share" in text:
        return "🔁 Click Share button."

    elif "delete" in text:
        return "🗑️ Use Delete button to remove your post."

    elif "help" in text:
        return "You can say: create post, like, comment, share."

    else:
        return "🤖 Try saying: create post, like, comment, share."