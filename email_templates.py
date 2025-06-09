# email_templates.py

EMAIL_TEMPLATES = {
    "weapon": """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Alert: Weapon Detected</title>
    </head>
    <body style="margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#F3F4F6;font-family:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;color:#374151;">
        <div class="container" style="width:100%;max-width:600px;margin:0 auto;padding:20px;">
            <div class="card" style="background-color:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;overflow:hidden;">
                <div class="header" style="padding:24px;border-bottom:1px solid #E5E7EB;">
                    <p class="header-title" style="margin:0;font-size:20px;font-weight:700;color:#111827;">
                        <span class="alert-icon" style="display:inline-block;width:20px;height:20px;margin-right:8px;vertical-align:middle;background-color:#DC2626;border-radius:50%;"></span>Security Alert
                    </p>
                </div>
                <div class="content" style="padding:24px;font-size:16px;line-height:1.6;">
                    <h2 style="margin:0 0 8px;font-size:24px;font-weight:700;color:#DC2626;">Weapon Detected</h2>
                    <p style="margin:0 0 24px;">The automated surveillance system has detected a <strong>weapon</strong>. Immediate action and verification are crucial for site security and personnel safety.</p>
                    
                    <table class="details" style="width:100%;margin-bottom:24px;">
                        <tr>
                            <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Timestamp:</th>
                            <td style="text-align:left;padding:8px 0;vertical-align:top;">{timestamp}</td>
                        </tr>
                        <tr>
                            <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Source:</th>
                            <td style="text-align:left;padding:8px 0;vertical-align:top;">{source}</td>
                        </tr>
                    </table>
    
                    <div class="emergency-contacts-box" style="background-color:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:15px 20px;margin-bottom:24px;font-size:15px;line-height:1.5;">
                        <p style="margin:5px 0;font-weight:600;color:#495057;"><strong>Emergency Contacts:</strong></p>
                        <p style="margin:5px 0;font-weight:600;color:#495057;">Police: <span style="font-weight:normal;color:#374151;">100</span></p>
                        <p style="margin:5px 0;font-weight:600;color:#495057;">National Emergency No.: <span style="font-weight:normal;color:#374151;">112</span></p>
                    </div>
    
                    <p class="image-caption" style="font-size:14px;color:#6B7280;margin-bottom:8px;text-align:center;">System-captured Image</p>
                    <img src="cid:detection_img" alt="Weapon Detection" class="detection-image" style="display:block;width:100%;max-width:100%;height:auto;border:1px solid #E5E7EB;border-radius:6px;margin-bottom:24px;">
    
                </div>
                <div class="footer" style="padding:24px;text-align:center;font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;margin-top:24px;">
                    <p style="margin:0;">This is an automated notification from the Intelligent Video Surveillance System.</p>
                    <p style="margin:0;">&copy; 2025 Intelligent Video Surveillance. All Rights Reserved. | <a href="mailto:intelligentvideosurveillance@gmail.com" style="color:#6B7280;text-decoration:underline;">Contact Support</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """,
    "fire": """
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Critical Alert: Fire Detected!</title>
        </head>
        <body style="margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#F3F4F6;font-family:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;color:#374151;">
            <div class="container" style="width:100%;max-width:600px;margin:0 auto;padding:20px;">
                <div class="card" style="background-color:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;overflow:hidden;">
                    <div class="header" style="padding:24px;border-bottom:1px solid #E5E7EB;">
                        <p class="header-title" style="margin:0;font-size:20px;font-weight:700;color:#111827;">
                            <span class="alert-icon" style="display:inline-block;width:20px;height:20px;margin-right:8px;vertical-align:middle;background-color:#FF4500;border-radius:50%;"></span>Security Alert
                        </p>
                    </div>
                    <div class="content" style="padding:24px;font-size:16px;line-height:1.6;">
                        <h2 style="margin:0 0 8px;font-size:24px;font-weight:700;color:#FF4500;">Fire Detected</h2>
                        <p style="margin:0 0 24px;">The automated surveillance system has identified a <strong>fire</strong>. Please verify the situation and contact emergency services if necessary.</p>
                        
                        <table class="details" style="width:100%;margin-bottom:24px;">
                            <tr>
                                <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Timestamp:</th>
                                <td style="text-align:left;padding:8px 0;vertical-align:top;">{timestamp}</td>
                            </tr>
                            <tr>
                                <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Source:</th>
                                <td style="text-align:left;padding:8px 0;vertical-align:top;">{source}</td>
                            </tr>
                        </table>
        
                        <div class="emergency-contacts-box" style="background-color:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:15px 20px;margin-bottom:24px;font-size:15px;line-height:1.5;">
                            <p style="margin:5px 0;font-weight:600;color:#495057;"><strong>Emergency Contacts:</strong></p>
                            <p style="margin:5px 0;font-weight:600;color:#495057;">Fire: <span style="font-weight:normal;color:#374151;">101</span></p>
                            <p style="margin:5px 0;font-weight:600;color:#495057;">National Emergency No.: <span style="font-weight:normal;color:#374151;">112</span></p>
                        </div>
        
                        <p class="image-caption" style="font-size:14px;color:#6B7280;margin-bottom:8px;text-align:center;">System-captured Image</p>
                        <img src="cid:detection_img" alt="Fire Detection" class="detection-image" style="display:block;width:100%;max-width:100%;height:auto;border:1px solid #E5E7EB;border-radius:6px;margin-bottom:24px;">
        
                    </div>
                    <div class="footer" style="padding:24px;text-align:center;font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;margin-top:24px;">
                        <p style="margin:0;">This is an automated notification from the Intelligent Video Surveillance System.</p>
                        <p style="margin:0;">&copy; 2025 Intelligent Video Surveillance. All Rights Reserved. | <a href="mailto:intelligentvideosurveillance@gmail.com" style="color:#6B7280;text-decoration:underline;">Contact Support</a></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """,
    "accident": """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Incident Alert: Accident Detected</title>
    </head>
    <body style="margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#F3F4F6;font-family:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;color:#374151;">
        <div class="container" style="width:100%;max-width:600px;margin:0 auto;padding:20px;">
            <div class="card" style="background-color:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;overflow:hidden;">
                <div class="header" style="padding:24px;border-bottom:1px solid #E5E7EB;">
                    <p class="header-title" style="margin:0;font-size:20px;font-weight:700;color:#111827;">
                        <span class="alert-icon" style="display:inline-block;width:20px;height:20px;margin-right:8px;vertical-align:middle;background-color:#FFA500;border-radius:50%;"></span>Security Alert
                    </p>
                </div>
                <div class="content" style="padding:24px;font-size:16px;line-height:1.6;">
                    <h2 style="margin:0 0 8px;font-size:24px;font-weight:700;color:#FFA500;">Accident Detected</h2>
                    <p style="margin:0 0 24px;">The automated surveillance system has identified a <strong>vehicle accident</strong> that requires immediate attention. Please review the attached image to assess the situation and dispatch necessary assistance promptly.</p>
                    
                    <table class="details" style="width:100%;margin-bottom:24px;">
                        <tr>
                            <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Timestamp:</th>
                            <td style="text-align:left;padding:8px 0;vertical-align:top;">{timestamp}</td>
                        </tr>
                        <tr>
                            <th style="text-align:left;padding:8px 0;vertical-align:top;font-weight:600;color:#6B7280;width:150px;">Source:</th>
                            <td style="text-align:left;padding:8px 0;vertical-align:top;">{source}</td>
                        </tr>
                    </table>
    
                    <div class="emergency-contacts-box" style="background-color:#f8f9fa;border:1px solid #e9ecef;border-radius:6px;padding:15px 20px;margin-bottom:24px;font-size:15px;line-height:1.5;">
                        <p style="margin:5px 0;font-weight:600;color:#495057;"><strong>Emergency Contacts:</strong></p>
                        <p style="margin:5px 0;font-weight:600;color:#495057;">Ambulance: <span style="font-weight:normal;color:#374151;">108</span></p>
                        <p style="margin:5px 0;font-weight:600;color:#495057;">National Emergency No.: <span style="font-weight:normal;color:#374151;">112</span></p>
                    </div>
    
                    <p class="image-caption" style="font-size:14px;color:#6B7280;margin-bottom:8px;text-align:center;">System-captured Image</p>
                    <img src="cid:detection_img" alt="Accident Detection" class="detection-image" style="display:block;width:100%;max-width:100%;height:auto;border:1px solid #E5E7EB;border-radius:6px;margin-bottom:24px;">
    
                </div>
                <div class="footer" style="padding:24px;text-align:center;font-size:12px;color:#9CA3AF;border-top:1px solid #E5E7EB;margin-top:24px;">
                    <p style="margin:0;">This is an automated notification from the Intelligent Video Surveillance System.</p>
                    <p style="margin:0;">&copy; 2025 Intelligent Video Surveillance. All Rights Reserved. | <a href="mailto:intelligentvideosurveillance@gmail.com" style="color:#6B7280;text-decoration:underline;">Contact Support</a></p>
                </div>
            </div>
        </div>
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
