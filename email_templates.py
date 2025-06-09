# email_templates.py

EMAIL_TEMPLATES = {
    "weapon": """
    <html>
    <body>
        <h2 style="color: #BF616A;">Weapon Detection Alert!</h2>
        <p>A potential weapon has been detected by the surveillance system.</p>
        <p><b>Time of Detection:</b> {timestamp}</p>
        <p><b>Video Source:</b> {source}</p>
        <p>Please review the attached image immediately and take appropriate action.</p>
        <br>
        <img src="cid:detection_img">
    </body>
    </html>
    """,
    "fire": """
    <html>
    <body>
        <h2 style="color: #D08770;">Fire Detection Alert!</h2>
        <p>A potential fire has been detected.</p>
        <p><b>Time of Detection:</b> {timestamp}</p>
        <p><b>Video Source:</b> {source}</p>
        <p>Immediate attention is required. Please verify the situation and contact emergency services if necessary.</p>
        <br>
        <img src="cid:detection_img">
    </body>
    </html>
    """,
    "accident": """
    <html>
    <body>
        <h2 style="color: #EBCB8B;">Accident Detection Alert!</h2>
        <p>A potential traffic accident has been detected.</p>
        <p><b>Time of Detection:</b> {timestamp}</p>
        <p><b>Video Source:</b> {source}</p>
        <p>Please review the attached image and dispatch help if needed.</p>
        <br>
        <img src="cid:detection_img">
    </body>
    </html>
    """,
    "object": """
    <html>
    <body>
        <h2 style="color: #A3BE8C;">Object Detection Alert!</h2>
        <p>A specific object of interest has been detected.</p>
        <p><b>Time of Detection:</b> {timestamp}</p>
        <p><b>Video Source:</b> {source}</p>
        <br>
        <img src="cid:detection_img">
    </body>
    </html>
    """
}