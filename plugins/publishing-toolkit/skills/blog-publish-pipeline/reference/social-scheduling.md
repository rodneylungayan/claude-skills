# Scheduling the social post

Goal: a **scheduled** post with the infographic attached, going out at the
profile's offset after the post went live. The steps below are written against
LinkedIn's composer, which is the awkward case; other networks are simpler but
the same cautions apply.

## 1. Work out the time

The publish timestamp from the backend is in UTC. Add the profile's offset,
then convert to the user's timezone.

Check the real clock first rather than computing from memory — `date -u`,
`TZ=<profile timezone> date`, and `new Date()` in the browser. A post scheduled
a day out because of a timezone assumption is not noticed until it is too late.

Most composers use 15-minute steps, so **round up** to the next slot and never
earlier than the offset. Tell the user the exact time you picked.

## 2. Use the right account

Stay in the browser profile the profile file names. If a sign-in page appears,
or the account is not the user's, **stop and ask**. Never enter passwords, and
never switch profiles to get around a sign-in.

## 3. Paste the text with its line breaks intact

LinkedIn's composer is a tiptap/ProseMirror editor at
`[contenteditable="true"][role="textbox"]`. A plain paste event silently drops
the blank lines, which collapses the post into one block of text.

What works: focus the editor, then

```js
document.execCommand('selectAll');
document.execCommand('delete');
// then, for each line of the post:
document.execCommand('insertParagraph');          // blank lines stay as empty paragraphs
document.execCommand('insertText', false, line);
```

Read the text back and compare it with the reviewed version. The `Read here:`
line and its URL must be intact. Use `insertText` for hashtags too — typing `#`
by hand opens a suggestion popup that eats the next keystrokes.

## 4. Remove the link preview card

The composer auto-adds a preview card for the post URL, and **while that card
is there the photo button is hidden**. Click the round X on the card first. The
URL stays in the text.

This is the step that most often looks like "the image button is missing".

## 5. Attach the infographic

Stage the PNG somewhere the browser tooling is allowed to read. Sandbox output
folders and raw host paths are usually rejected; a staged uploads path is
accepted.

The photo button builds its `<input type="file">` only when clicked, so a
search of the page finds only a button. Before clicking it, patch the page:

```js
if (!window.__ccPatched) {
  window.__ccPatched = true;
  const orig = HTMLInputElement.prototype.click;
  HTMLInputElement.prototype.click = function () {
    if (this.type === 'file') {       // give it an id and keep the native picker shut
      this.id = '__cc_file';
      document.body.appendChild(this);
      return;
    }
    return orig.apply(this, arguments);
  };
}
```

Then click the photo icon, wait a few seconds for the dialog, find
`#__cc_file`, and upload the staged path to it.

Check the preview shows the **infographic** and not the cover, then click
Next. Re-apply the patch after any navigation.

## 6. Schedule, never post

Click the clock icon next to the Post button. The dialog has a date field and a
time dropdown in 15-minute steps. Pick the slot, confirm, and the main button
changes to **Schedule**. Click that.

**Do not click the normal Post button.** If the clock icon is missing, stop and
report rather than posting now.

## 7. Verify

Open the scheduled posts list. It should show the entry with its date and time,
the first lines of the text, and the image thumbnail. Screenshot it for the
report, then close the dialog.

## If it fails

Do not post immediately as a fallback. Hand the text and the image back ready
to copy, say exactly which step failed, and let the user decide. A post that
goes out eight hours early is a worse outcome than one posted by hand.

As a last resort for the image alone, paste the PNG with a JavaScript paste
event carrying a `File` built from the base64 image, or ask the user to drag it
in themselves.
