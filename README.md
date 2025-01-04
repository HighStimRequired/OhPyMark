# **OhPyMark**

A Powerful, Modern, and User-Friendly Markdown Editor

OhPyMark is a full-featured Markdown editor designed to boost your productivity and creativity. Featuring **live preview**, **rich text formatting**, **autosave**, and **file watching**, OhPyMark delivers a smooth editing experience for writers, developers, and anyone who loves Markdown.

## **Key Features**

1. **Modern UI**

   * Sleek split-view interface: Markdown on the left, **live preview** on the right.
   * Multiple **themes** (Light, Dark, Solarized, High Contrast) to suit your environment.
   * Convenient **toolbar** and right-click **context menu** for quick formatting.

2. **Rich Formatting Options**

   * One-click **bold**, **italic**, **strikethrough**, **inline code**, **code blocks**, **headings**, and more.
   * Support for **bullet lists**, **numbered lists**, **blockquotes**, and **tables**.
   * Easy **image embedding** and **link insertion**.

3. **Advanced Text Management**

   * **Find & Replace** dialog for quick text editing.
   * **Autosave** feature keeps your work safe—automatically creates `.autosave` files.
   * Optional **file watcher** reloads if a file is changed externally (with user confirmation).

4. **Export & Sharing**

   * **Export to HTML** with syntax highlighting (via `pymdown-extensions`).
   * **Export to PDF** (powered by `pdfkit` + `wkhtmltopdf`).
   * Compatible with various external tools and workflows.

5. **Simple Preferences**

   * Adjust background color and fine-tune your environment in the **Preferences** dialog.
   * Fully customizable to meet your personal or professional needs.

## **Why OhPyMark?**

* **Productivity-First**: Instant live preview, easily accessible formatting actions, and helpful auto-features let you focus on writing.
* **Beginner-Friendly**: Straightforward interface with minimal setup—start writing Markdown right away!
* **Advanced Markdown Capabilities**: Leverage powerful `pymdown-extensions` for code highlighting and extended Markdown syntax.

## **Getting Started**

1. **Install Requirements**

   ```bash
   pip install PyQt5 markdown pymdown-extensions pdfkit
   ```

   Also install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) if you plan to export PDFs.

2. **Run the Editor**

   ```bash
   python OhPyMark.py
   ```

3. **Start Editing!**

   * Use the **File** menu to open or create a new Markdown file.
   * Type Markdown on the left and watch the **live preview** on the right.
   * Apply formatting via the **toolbar** or **Format** menu.

## **Contributing**

I welcome contributions! Feel free to open issues, suggest new features, or submit pull requests.

## **License**

This project is licensed under the MIT License — see the [LICENSE](https://chatgpt.com/c/LICENSE) file for details.

***

**Enjoy a faster, smarter, and more intuitive Markdown editing experience with OhPyMark!**
