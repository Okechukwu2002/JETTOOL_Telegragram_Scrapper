# #
# # import asyncio
# # import csv
# # import phonenumbers
# # from phonenumbers import geocoder, PhoneNumberFormat
# #
# # import os
# # import paramiko
# # import random
# # import re
# # import threading
# # import time
# # import uuid
# # from datetime import datetime, timedelta
# # from flask import (Flask, abort, flash, jsonify, redirect, render_template,
# #                    render_template_string, request, send_file, session, url_for, send_from_directory, current_app, app)
# # from telethon.tl.functions.channels import InviteToChannelRequest
# # from werkzeug.exceptions import NotFound
# # from werkzeug.utils import secure_filename
# # from telethon import TelegramClient
# # from telethon.tl.functions.contacts import ImportContactsRequest
# # from telethon.tl.functions.messages import SendMessageRequest
# # from telethon.tl.functions.users import GetFullUserRequest
# # from telethon.tl.types import InputPhoneContact
# # from telethon.errors import (
# #     FloodWaitError,
# #     PeerFloodError,
# #     SessionPasswordNeededError,
# #     UserPrivacyRestrictedError
# # )
# #
# # import pandas as pd
# # from docx import Document
# # import logging
# # from reportlab.lib import colors
# #
# #
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s [%(levelname)s] %(message)s"
# # )
# #
# # logger = logging.getLogger("JETTOOL")
# #
# #
# #
# # os.makedirs("logs", exist_ok=True)
# # os.makedirs("reports", exist_ok=True)
# #
# #
# #
# #
# # os.makedirs("logs", exist_ok=True)
# # os.makedirs("reports", exist_ok=True)
# #
# #
# #
# #
# # WORDLIST_PATH = os.path.join(os.path.dirname(__file__), "wordlists", "common_100k.txt")
# #
# # # Global fallback wordlist (used if file missing or task_manager not ready)
# # FALLBACK_PASSWORDS = [
# #                          "123456", "password", "123456789", "12345678", "12345", "qwerty", "abc123", "Password",
# #                          "111111", "123123", "admin123", "admin", "letmein", "welcome", "monkey", "sunshine",
# #                          "princess", "1234567", "1234567890", "password123", "iloveyou", "trustno1"
# #                      ] * 500  # 10,000 entries
# #
# #
# # COMMON_PASSWORDS = FALLBACK_PASSWORDS
# #
# #
# # app = Flask(__name__)
# #
# #
# #
# # class TaskManager:
# #     _instance = None
# #     _lock = threading.Lock()
# #
# #     def __new__(cls):
# #         if cls._instance is None:
# #             with cls._lock:
# #                 if cls._instance is None:
# #                     cls._instance = super().__new__(cls)
# #                     cls._instance.tasks = {}
# #                     cls._instance.loop = None
# #                     cls._instance._start_loop()
# #         return cls._instance
# #
# #     def _start_loop(self):
# #         def run():
# #             loop = asyncio.new_event_loop()
# #             asyncio.set_event_loop(loop)
# #             self.loop = loop
# #             loop.run_forever()
# #
# #         thread = threading.Thread(target=run, daemon=True, name="JETTOOL-AsyncLoop")
# #         thread.start()
# #         time.sleep(0.5)
# #         logger.info("JETTOOL Async Loop Started — TaskManager Ready")
# #
# #     # === CRITICAL: THIS METHOD WAS MISSING — NOW ADDED ===
# #     def create_task(self, name="Task", target="", current="Initializing...", progress=0):
# #         """
# #         Create a new task entry safely and return task_id
# #         Used before launching scans to avoid race conditions
# #         """
# #         task_id = str(uuid.uuid4())
# #         with self._lock:
# #             self.tasks[task_id] = {
# #                 "name": name,
# #                 "target": target,
# #                 "current": current,
# #                 "progress": progress,
# #                 "status": "running",
# #                 "result": None,
# #                 "report": None,
# #                 "created": datetime.now().isoformat(),
# #                 "completed": None,
# #                 "logs": [],
# #                 "user_id": None  # Will be set by route after creation
# #             }
# #         logger.info(f"Task created: {task_id[:8]} — {name}")
# #         return task_id
# #
# #     def run_task(self, coro_factory):
# #         """
# #         Launch an async task and return task_id immediately
# #         coro_factory: lambda task_id: your_coroutine(...)
# #         """
# #         task_id = str(uuid.uuid4())
# #
# #         # Create coroutine from factory
# #         coro = coro_factory(task_id)
# #
# #         # Submit to background loop
# #         future = asyncio.run_coroutine_threadsafe(coro, self.loop)
# #
# #         # Initialize task storage
# #         with self._lock:
# #             self.tasks[task_id] = {
# #                 "future": future,
# #                 "status": "running",
# #                 "progress": 0,
# #                 "current": "Starting scan...",
# #                 "created": datetime.now().isoformat(),
# #                 "target": None,
# #                 "result": None,
# #                 "report": None,
# #                 "logs": [],
# #                 "user_id": None
# #             }
# #
# #         # Completion callback
# #         def on_done(fut):
# #             with self._lock:
# #                 if task_id not in self.tasks:
# #                     return
# #                 try:
# #                     result = fut.result()
# #                     self.tasks[task_id]["result"] = result
# #                     self.tasks[task_id]["status"] = "completed"
# #                 except Exception as e:
# #                     self.tasks[task_id]["error"] = str(e)
# #                     self.tasks[task_id]["status"] = "failed"
# #                 finally:
# #                     self.tasks[task_id]["completed"] = datetime.now().isoformat()
# #
# #         future.add_done_callback(on_done)
# #
# #         logger.info(f"Task launched: {task_id[:8]}")
# #         return task_id
# #
# #     def get_status(self, task_id: str):
# #         """Return clean, JSON-safe task status"""
# #         with self._lock:
# #             task = self.tasks.get(task_id)
# #             if not task:
# #                 return {"status": "not_found"}
# #
# #             safe_task = {
# #                 "status": task.get("status", "unknown"),
# #                 "progress": task.get("progress", 0),
# #                 "current": task.get("current", "Unknown"),
# #                 "target": task.get("target"),
# #                 "created": task.get("created"),
# #                 "completed": task.get("completed"),
# #                 "logs": task.get("logs", [])[-50:],
# #                 "report": task.get("report")
# #             }
# #
# #             if task.get("status") == "completed" and task.get("result"):
# #                 safe_task["result"] = task["result"]
# #             elif task.get("status") == "failed":
# #                 safe_task["error"] = task.get("error", "Unknown error")
# #
# #             # Optional: include user_id for security checks
# #             safe_task["user_id"] = task.get("user_id")
# #
# #             return safe_task
# #
# #     def update_progress(self, task_id: str, progress: int, current: str):
# #         """Update progress and message"""
# #         with self._lock:
# #             if task_id in self.tasks:
# #                 self.tasks[task_id]["progress"] = max(0, min(100, int(progress)))
# #                 self.tasks[task_id]["current"] = str(current)[:200]
# #
# #     def log(self, task_id: str, message: str, level: str = "info"):
# #         """Log message for task"""
# #         with self._lock:
# #             if task_id in self.tasks:
# #                 entry = {
# #                     "time": datetime.now().isoformat(),
# #                     "message": str(message)
# #                 }
# #                 self.tasks[task_id]["logs"].append(entry)
# #                 getattr(logger, level)(f"[TASK {task_id[:8]}] {message}")
# #
# # # Global instance
# # task_manager = TaskManager()
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# # @app.route("/", methods=["GET", "POST"])
# # def telegram_extractor():
# #     if request.method == "POST":
# #         target = request.form.get("target", "").strip()
# #         if not target:
# #             flash("Target is required!", "error")
# #             return redirect(url_for('telegram_extractor'))
# #
# #         options = {k: k in request.form for k in [
# #             "aggressive", "include_phone", "include_bio", "include_premium",
# #             "include_last_seen", "include_names", "include_photos", "add_to_contacts"
# #         ]}
# #
# #         def factory(task_id):
# #             return telegram_member_extractor(target=target, options=options, task_id=task_id)
# #
# #         task_id = task_manager.run_task(factory)
# #         return redirect(url_for('telegram_extractor_status', task_id=task_id))
# #
# #     return render_template("telegram_extractor.html")
# #
# # @app.route("/<task_id>")
# # def telegram_extractor_status(task_id):
# #     with task_manager._lock:
# #         if task_id not in task_manager.tasks:
# #             flash("Task not found.", "error")
# #             return redirect(url_for('telegram_extractor'))
# #     return render_template("telegram_extractor_status.html")
# #
# # async def telegram_member_extractor(target: str, options: dict, task_id: str):
# #     """
# #     JETTOOL ULTIMATE v2025 — TRUE DYNAMIC EXTRACTION
# #     Uses StringSession with saved string → NO MORE LOGIN PROMPTS EVER
# #     """
# #     api_id = 34339995
# #     api_hash = "7f73fa5feb68553394202e1e654b545d"
# #
# #     # === PASTE YOUR SESSION STRING HERE (from first successful run) ===
# #     SAVED_SESSION = "1BJWap1sBu1uT_DRyPhsJRwOxfKF55_JK_GgfAA6lvHW9j2MBvrrM-wM7uiNlItiPd8cJ7cTueoXVwGJ803eMbaWhoQvJl3rVhJ0cteYZ6S-kkshSrel615SgF59Ikgv2hfkJcI63JGV0An3LGfSbV2ZJav0Bk5888OHKotVsvvUjWrKaYu08FVAK4DHMj1Iuv9gtuUvj26FlX52jbvcQzMZ_cCaB4Vd2ZGjMkuA9QRhRbvhQg4Pcr5UZJXeImDrczEXQdb6Bxc68dxwnmsz9U-HCVs4QY2RWD18ktp5hv_smPIV0IhV7-Cn7i_NAmOqj_MQv44HSXbNFsBpvPgvougS3dC8RO3Q="
# #
# #     HISTORY_SCAN_LIMIT = 50000
# #
# #     result = {
# #         "total": 0,
# #         "success": False,
# #         "members": [],
# #         "added_to_contacts": 0,
# #         "friend_requests_sent": 0,
# #         "failed_adds": 0,
# #         "added_to_my_group": 0,
# #         "extracted_emails": set(),
# #         "extracted_phones": set(),
# #         "reports": {}
# #     }
# #
# #     def update(progress: int, msg: str):
# #         task_manager.update_progress(task_id, progress, msg)
# #         task_manager.log(task_id, msg, "info")
# #
# #     def log_error(msg: str):
# #         task_manager.log(task_id, f"ERROR: {msg}", "error")
# #
# #     update(5, "Initializing permanent session...")
# #
# #     from telethon.sessions import StringSession
# #
# #     # Use saved session if available, otherwise create new (will print string on first run)
# #     if SAVED_SESSION.strip():
# #         client = TelegramClient(StringSession(SAVED_SESSION), api_id, api_hash)
# #     else:
# #         client = TelegramClient(StringSession(), api_id, api_hash)
# #
# #     try:
# #         await client.start()
# #
# #         # FIRST TIME ONLY: Print session string to console
# #         if not SAVED_SESSION.strip():
# #             session_string = client.session.save()
# #             print("\n" + "="*100)
# #             print("FIRST-TIME LOGIN SUCCESS! COPY THIS SESSION STRING NOW:")
# #             print("="*100)
# #             print(session_string)
# #             print("="*100)
# #             print("Paste it into SAVED_SESSION variable above,")
# #             print("save the file, and restart the app → NEVER login again!")
# #             print("="*100 + "\n")
# #
# #         update(20, "Authenticated successfully — ready to extract!")
# #     except Exception as e:
# #         log_error(f"Authentication failed: {str(e)}")
# #         update(100, "Failed: Could not authenticate")
# #         return result
# #
# #     # === REST OF YOUR CODE (UNCHANGED FROM HERE) ===
# #     try:
# #         update(30, f"Resolving target: {target}")
# #         entity = await client.get_entity(target)
# #         entity_title = getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))
# #         update(40, f"Target resolved: {entity_title}")
# #
# #         update(50, "Fetching members...")
# #         members = []
# #
# #         try:
# #             direct_members = await client.get_participants(entity, limit=0, aggressive=options.get("aggressive", False))
# #             if len(direct_members) > 0:
# #                 members = direct_members
# #                 update(55, f"Direct fetch: {len(members)} members found instantly")
# #             else:
# #                 update(55, "No visible members — discovering active users from history...")
# #         except Exception:
# #             update(55, "Direct fetch unavailable — discovering active users from history...")
# #
# #         if len(members) == 0:
# #             seen_users = set()
# #             email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
# #             phone_regex = re.compile(r'\+?\d{10,15}')
# #
# #             msg_count = 0
# #
# #             async for message in client.iter_messages(entity, limit=HISTORY_SCAN_LIMIT):
# #                 msg_count += 1
# #
# #                 if message.message:
# #                     result["extracted_emails"].update(email_regex.findall(message.message))
# #                     result["extracted_phones"].update(phone_regex.findall(message.message))
# #
# #                 if message.sender_id and message.sender_id not in seen_users:
# #                     try:
# #                         user = await client.get_entity(message.sender_id)
# #                         seen_users.add(message.sender_id)
# #                         members.append(user)
# #
# #                         if len(seen_users) % 50 == 0:
# #                             update(55 + int((msg_count / HISTORY_SCAN_LIMIT) * 30),
# #                                    f"Discovering active users... Found {len(seen_users)} so far")
# #                     except:
# #                         pass
# #
# #                 if msg_count % 5000 == 0:
# #                     update(55 + int((msg_count / HISTORY_SCAN_LIMIT) * 30),
# #                            f"Scanning history: {msg_count:,} messages | {len(seen_users)} users discovered")
# #
# #             update(85, f"Discovery complete: {len(members)} active users found!")
# #
# #         total_members = len(members)
# #         result["total"] = total_members
# #         update(86, f"Processing {total_members} discovered members...")
# #
# #         processed = added = friend_sent = failed = 0
# #
# #         if options.get("include_photos"):
# #             os.makedirs("static/profile_photos", exist_ok=True)
# #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #
# #         processed = added = friend_sent = failed = 0
# #
# #         for entity in members:
# #             processed += 1
# #
# #             # SAFETY: Only process actual users
# #             if not hasattr(entity, 'first_name') or entity.is_self or entity.deleted or entity.bot:
# #                 continue
# #
# #             user = entity  # It's already a User object
# #
# #             prog = 86 + int((processed / total_members) * 10) if total_members > 0 else 96
# #             if processed % 50 == 0 or processed == total_members:
# #                 update(prog, f"Processing {processed}/{total_members} | +{added} contacts | +{friend_sent} requests")
# #
# #             member_data = {"User ID": user.id}
# #
# #             if options.get("include_names", True):
# #                 member_data["Username"] = f"@{user.username}" if user.username else "None"
# #                 member_data["Full Name"] = f"{user.first_name or ''} {user.last_name or ''}".strip() or "None"
# #
# #             raw_phone = user.phone or "Hidden"
# #             formatted_phone = raw_phone
# #             country = "Unknown"
# #
# #             if raw_phone != "Hidden" and raw_phone:
# #                 try:
# #                     # Parse phone (assume default region if needed, here 'NG' for Nigeria as fallback)
# #                     parsed = phonenumbers.parse(raw_phone,
# #                                                 "NG")  # Change "NG" if your targets are mostly from another country
# #
# #                     # Format with +country code
# #                     formatted_phone = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
# #
# #                     # Get country name
# #                     country_desc = geocoder.description_for_number(parsed, "en")
# #                     country = country_desc or "Unknown"
# #                 except Exception:
# #                     formatted_phone = raw_phone
# #                     country = "Invalid Format"
# #
# #             member_data["Phone"] = formatted_phone
# #             member_data["Country"] = country
# #
# #             if options.get("include_premium"):
# #                 member_data["Premium"] = "Yes" if getattr(user, 'premium', False) else "No"
# #
# #             if options.get("include_last_seen"):
# #                 status_str = str(user.status) if user.status else ""
# #                 member_data["Last Seen"] = (
# #                     "Online" if "Online" in status_str else
# #                     "Recently" if "Recently" in status_str else
# #                     "Last week" if "LastWeek" in status_str else
# #                     "Last month" if "LastMonth" in status_str else
# #                     "Hidden"
# #                 )
# #
# #             if options.get("include_bio"):
# #                 try:
# #                     full_user = await client(GetFullUserRequest(user))
# #                     member_data["Bio"] = getattr(full_user.full_user, 'about', '') or "No bio"
# #                 except:
# #                     member_data["Bio"] = "Unavailable"
# #
# #             # Photo download (safe)
# #             member_data["Photo URL"] = ""
# #             if options.get("include_photos"):
# #                 try:
# #                     photos = await client.get_profile_photos(user, limit=1)
# #                     if photos:
# #                         photo_filename = f"{user.id}_{timestamp}.jpg"
# #                         photo_path = os.path.join("static", "profile_photos", photo_filename)
# #                         await client.download_media(photos[0], photo_path)
# #                         member_data["Photo URL"] = f"/static/profile_photos/{photo_filename}"
# #                 except Exception as e:
# #                     pass  # Silent fail on photo
# #
# #             result["members"].append(member_data)
# #
# #             # Add to contacts / send message (only real users with phone or visible)
# #             if options.get("add_to_contacts"):
# #                 try:
# #                     if user.phone:
# #                         contact = InputPhoneContact(client_id=0, phone=user.phone,
# #                                                     first_name=user.first_name or "User",
# #                                                     last_name=user.last_name or "")
# #                         await client(ImportContactsRequest([contact]))
# #                         added += 1
# #                     else:
# #                         await client.send_message(user, "Hi! Connected via community 👋")
# #                         friend_sent += 1
# #                     await asyncio.sleep(random.uniform(2, 4))
# #                 except UserPrivacyRestrictedError:
# #                     failed += 1
# #                 except FloodWaitError as e:
# #                     log_error(f"Flood wait: {e.seconds}s")
# #                     await asyncio.sleep(e.seconds + 10)
# #                 except Exception:
# #                     failed += 1
# #
# #         result["added_to_contacts"] = added
# #         result["friend_requests_sent"] = friend_sent
# #         result["failed_adds"] = failed
# #
# #         my_group_link = options.get("my_group", "").strip()
# #         if my_group_link and total_members > 0:
# #             update(96, "Preparing to add users to your group...")
# #             try:
# #                 my_entity = await client.get_entity(my_group_link)
# #                 my_title = getattr(my_entity, 'title', 'Your Group')
# #                 update(97, f"Inviting {total_members} users to: {my_title}...")
# #
# #                 added_to_group = 0
# #                 for user in members:
# #                     try:
# #                         await client(InviteToChannelRequest(channel=my_entity, users=[user]))
# #                         added_to_group += 1
# #                         if added_to_group % 10 == 0:
# #                             update(97 + int((added_to_group / total_members) * 2),
# #                                    f"Adding to your group: {added_to_group}/{total_members} invited")
# #                         await asyncio.sleep(random.uniform(2.5, 5.0))
# #                     except UserPrivacyRestrictedError:
# #                         pass
# #                     except FloodWaitError as e:
# #                         update(98, f"Flood wait {e.seconds}s")
# #                         await asyncio.sleep(e.seconds + 20)
# #                     except Exception:
# #                         pass
# #
# #                 result["added_to_my_group"] = added_to_group
# #             except Exception as e:
# #                 log_error(f"Group invite failed: {str(e)}")
# #
# #         update(98, "Generating professional reports...")
# #
# #         reports_dir = "reports"
# #         os.makedirs(reports_dir, exist_ok=True)
# #         safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in entity_title)[:50]
# #         base_name = f"JETTOOL_{safe_title}_{timestamp}"
# #
# #         if result["members"]:
# #             fieldnames = result["members"][0].keys()
# #
# #             csv_path = os.path.join(reports_dir, f"{base_name}.csv")
# #             with open(csv_path, "w", newline="", encoding="utf-8") as f:
# #                 writer = csv.DictWriter(f, fieldnames=fieldnames)
# #                 writer.writeheader()
# #                 writer.writerows(result["members"])
# #             result["reports"]["csv"] = f"{base_name}.csv"
# #
# #             xlsx_path = os.path.join(reports_dir, f"{base_name}.xlsx")
# #             df = pd.DataFrame(result["members"])
# #             df.to_excel(xlsx_path, index=False)
# #             result["reports"]["xlsx"] = f"{base_name}.xlsx"
# #
# #         with task_manager._lock:
# #             task_manager.tasks[task_id]["full_data"] = result["members"]
# #
# #         result["extracted_emails"] = sorted(list(result["extracted_emails"]))
# #         result["extracted_phones"] = sorted(list(result["extracted_phones"]))
# #
# #         result["success"] = True
# #
# #         final_msg = (f"SUCCESS: {total_members} extracted | {added} contacts | {friend_sent} requests | "
# #                      f"{result['added_to_my_group']} added to group | {len(result['extracted_emails'])} emails | "
# #                      f"{len(result['extracted_phones'])} phones")
# #         update(100, final_msg)
# #         task_manager.log(task_id, final_msg, "critical")
# #
# #     except Exception as e:
# #         log_error(f"Critical error: {str(e)}")
# #         update(100, "Extraction failed")
# #     finally:
# #         if client.is_connected():
# #             await client.disconnect()
# #
# #     return result
# #
# #
# # @app.route("/view-data/<task_id>")
# # def view_data(task_id):
# #     with task_manager._lock:
# #         if task_id not in task_manager.tasks or "full_data" not in task_manager.tasks[task_id]:
# #             flash("Data not available.", "error")
# #             return redirect(url_for('telegram_extractor'))
# #
# #         members = task_manager.tasks[task_id]["full_data"]
# #
# #     return render_template("view_data.html", members=members, task_id=task_id)
# #
# #
# #
# #
# #
# #
# #
# #
# #
# # #  RUN
# # if __name__ == "__main__":
# #     print("JETTOOL WEB PRO v2025 LAUNCHED")
# #     print("http://localhost:5000")
# #     app.run(host="0.0.0.0", port=5000, debug=False)
# #
# #
#
#
#
#
#
#
#
# import asyncio
# import os
# import uuid
# import threading
# import logging
# from datetime import datetime, timezone
#
# from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, send_from_directory
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
#
# import phonenumbers
# from phonenumbers import geocoder, PhoneNumberFormat
#
# from telethon import TelegramClient
# from telethon.sessions import StringSession
# from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
# from telethon.tl.types import User
#
# import csv
# from openpyxl import Workbook
#
# # -------------------------------------------------------------------
# # LOGGING
# # -------------------------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("JETTOOL")
#
# # -------------------------------------------------------------------
# # APP CONFIG
# # -------------------------------------------------------------------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
#
# app = Flask(__name__)
# app.secret_key = "jettool-secret-key"
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'jettool.db')}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
#
# # Create folders if not exist
# os.makedirs("logs", exist_ok=True)
# os.makedirs("reports", exist_ok=True)
# os.makedirs("static/profile_photos", exist_ok=True)
#
# # -------------------------------------------------------------------
# # DATABASE MODELS
# # -------------------------------------------------------------------
# class Task(db.Model):
#     id = db.Column(db.String(36), primary_key=True)
#     target = db.Column(db.String(255))
#     status = db.Column(db.String(20), default="running")
#     progress = db.Column(db.Integer, default=0)
#     current = db.Column(db.String(255), default="Initializing")
#     created = db.Column(db.DateTime, default=datetime.utcnow)
#     completed = db.Column(db.DateTime, nullable=True)
#     members = db.relationship("Member", backref="task", lazy=True)
#
#
# class Member(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     task_id = db.Column(db.String(36), db.ForeignKey("task.id"))
#     user_id = db.Column(db.BigInteger)
#     username = db.Column(db.String(100))
#     full_name = db.Column(db.String(200))
#     phone = db.Column(db.String(50))
#     country = db.Column(db.String(100))
#     premium = db.Column(db.String(10))
#     last_seen = db.Column(db.String(50))
#     bio = db.Column(db.Text, nullable=True)
#     photo_url = db.Column(db.String(255), nullable=True)
#
# # Ensure DB tables exist
# with app.app_context():
#     db.create_all()
#
# # -------------------------------------------------------------------
# # TASK MANAGER
# # -------------------------------------------------------------------
# class TaskManager:
#     def __init__(self):
#         self.loop = asyncio.new_event_loop()
#         threading.Thread(target=self.loop.run_forever, daemon=True).start()
#
#     def create_task(self, target):
#         task_id = str(uuid.uuid4())
#         db_task = Task(id=task_id, target=target)
#         db.session.add(db_task)
#         db.session.commit()
#         return task_id
#
#     def update(self, task_id, progress, msg):
#         task = db.session.get(Task, task_id)
#         if task:
#             task.progress = progress
#             task.current = msg
#             db.session.commit()
#
#     def complete(self, task_id):
#         task = db.session.get(Task, task_id)
#         if task:
#             task.status = "completed"
#             task.progress = 100
#             task.completed = datetime.now(timezone.utc)
#             db.session.commit()
#
#
# task_manager = TaskManager()
#
# # -------------------------------------------------------------------
# # ROUTES
# # -------------------------------------------------------------------
# @app.route("/", methods=["GET", "POST"])
# def telegram_extractor():
#     if request.method == "POST":
#         target = request.form.get("target", "").strip()
#         if not target:
#             flash("Target required", "error")
#             return redirect(url_for("telegram_extractor"))
#
#         task_id = task_manager.create_task(target)
#         asyncio.run_coroutine_threadsafe(
#             telegram_member_extractor(target, task_id),
#             task_manager.loop
#         )
#         return redirect(url_for("telegram_status", task_id=task_id))
#
#     return render_template("telegram_extractor.html")
#
#
# @app.route("/task-status/<task_id>")
# def task_status_api(task_id):
#     task = Task.query.get_or_404(task_id)
#     members_count = len(task.members)
#     added_to_contacts = sum(1 for m in task.members if m.phone != "Hidden")
#     friend_requests_sent = members_count  # Example: could be replaced with actual logic
#
#     return jsonify({
#         "status": task.status,
#         "progress": task.progress,
#         "current": task.current,
#         "completed": task.completed.isoformat() if task.completed else None,
#         "result": {
#             "total": members_count,
#             "added_to_contacts": added_to_contacts,
#             "friend_requests_sent": friend_requests_sent,
#             "success": task.status == "completed",
#             "members": [  # send full member data for downloads
#                 {
#                     "user_id": m.user_id,
#                     "username": m.username,
#                     "full_name": m.full_name,
#                     "phone": m.phone,
#                     "country": m.country,
#                     "premium": m.premium,
#                     "last_seen": m.last_seen,
#                     "bio": m.bio,
#                     "photo_url": m.photo_url
#                 } for m in task.members
#             ],
#             "reports": {
#                 "csv": f"{task.id}.csv" if members_count > 0 else None,
#                 "xlsx": f"{task.id}.xlsx" if members_count > 0 else None
#             }
#         },
#         "logs": []  # Add real-time log if you implement logging per task
#     })
#
#
# @app.route("/status/<task_id>")
# def telegram_status(task_id):
#     task = Task.query.get_or_404(task_id)
#     return render_template("telegram_extractor_status.html", task=task)
#
#
# @app.route("/view-data/<task_id>")
# def view_data(task_id):
#     task = Task.query.get_or_404(task_id)
#     return render_template("view_data.html", members=task.members, task_id=task_id)
#
#
# # -------------------------------------------------------------------
# # DOWNLOAD REPORTS
# # -------------------------------------------------------------------
# @app.route("/reports/<filename>")
# def download_report(filename):
#     filepath = os.path.join("reports", filename)
#     if os.path.exists(filepath):
#         return send_from_directory("reports", filename, as_attachment=True)
#     return "Report not found", 404
#
#
# # -------------------------------------------------------------------
# # TELEGRAM EXTRACTION WITH PROFILE PHOTOS
# # -------------------------------------------------------------------
# async def telegram_member_extractor(target, task_id):
#     api_id = 34339995
#     api_hash = "7f73fa5feb68553394202e1e654b545d"
#     SAVED_SESSION = "1BJWap1sBu1uT_DRyPhsJRwOxfKF55_JK_GgfAA6lvHW9j2MBvrrM-wM7uiNlItiPd8cJ7cTueoXVwGJ803eMbaWhoQvJl3rVhJ0cteYZ6S-kkshSrel615SgF59Ikgv2hfkJcI63JGV0An3LGfSbV2ZJav0Bk5888OHKotVsvvUjWrKaYu08FVAK4DHMj1Iuv9gtuUvj26FlX52jbvcQzMZ_cCaB4Vd2ZGjMkuA9QRhRbvhQg4Pcr5UZJXeImDrczEXQdb6Bxc68dxwnmsz9U-HCVs4QY2RWD18ktp5hv_smPIV0IhV7-Cn7i_NAmOqj_MQv44HSXbNFsBpvPgvougS3dC8RO3Q="
#
#     client = TelegramClient(StringSession(SAVED_SESSION), api_id, api_hash)
#
#     try:
#         await client.start()
#         task_manager.update(task_id, 20, "Authenticated")
#
#         entity = await client.get_entity(target)
#         members = await client.get_participants(entity)
#
#         total = len(members)
#         task_manager.update(task_id, 50, f"{total} members found")
#
#         report_csv = os.path.join("reports", f"{task_id}.csv")
#         report_xlsx = os.path.join("reports", f"{task_id}.xlsx")
#
#         # Excel workbook
#         wb = Workbook()
#         ws = wb.active
#         ws.title = "Members"
#         ws.append(["User ID", "Username", "Full Name", "Phone", "Country", "Premium", "Last Seen", "Bio", "Photo URL"])
#
#         csv_file = open(report_csv, "w", newline="", encoding="utf-8")
#         csv_writer = csv.writer(csv_file)
#         csv_writer.writerow(["User ID", "Username", "Full Name", "Phone", "Country", "Premium", "Last Seen", "Bio", "Photo URL"])
#
#         for i, user in enumerate(members, start=1):
#             if not isinstance(user, User) or user.bot or user.deleted:
#                 continue
#
#             phone = user.phone or "Hidden"
#             country = "Unknown"
#             bio = getattr(user, "about", "") or ""
#             photo_url = None
#
#             # Download profile photo if exists
#             if user.photo:
#                 filename = f"{task_id}_{user.id}.jpg"
#                 path = os.path.join("static/profile_photos", filename)
#                 try:
#                     await client.download_profile_photo(user, file=path)
#                     photo_url = url_for('static', filename=f"profile_photos/{filename}")
#                 except Exception as e:
#                     logger.warning(f"Failed to download photo for {user.id}: {e}")
#
#             if phone != "Hidden":
#                 try:
#                     parsed = phonenumbers.parse(phone, "NG")
#                     phone = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
#                     country = geocoder.description_for_number(parsed, "en")
#                 except:
#                     pass
#
#             member = Member(
#                 task_id=task_id,
#                 user_id=user.id,
#                 username=user.username,
#                 full_name=f"{user.first_name or ''} {user.last_name or ''}".strip(),
#                 phone=phone,
#                 country=country,
#                 premium="Yes" if getattr(user, "premium", False) else "No",
#                 last_seen=str(user.status),
#                 bio=bio,
#                 photo_url=photo_url
#             )
#             db.session.add(member)
#
#             csv_writer.writerow([member.user_id, member.username, member.full_name, member.phone, member.country,
#                                  member.premium, member.last_seen, member.bio, member.photo_url])
#             ws.append([member.user_id, member.username, member.full_name, member.phone, member.country,
#                        member.premium, member.last_seen, member.bio, member.photo_url])
#
#             if i % 50 == 0:
#                 task_manager.update(task_id, 50 + int((i / total) * 40), f"Processing {i}/{total}")
#
#         db.session.commit()
#         csv_file.close()
#         wb.save(report_xlsx)
#
#         task_manager.complete(task_id)
#
#     except (FloodWaitError, UserPrivacyRestrictedError) as e:
#         logger.warning(f"Telegram error: {e}")
#         task_manager.update(task_id, 0, f"Error: {e}")
#
#     except Exception as e:
#         logger.error(e)
#         task_manager.update(task_id, 0, f"Error: {e}")
#
#     finally:
#         await client.disconnect()
#
#
# # -------------------------------------------------------------------
# # RUN APP
# # -------------------------------------------------------------------
# if __name__ == "__main__":
#     print("JETTOOL WEB PRO v2025")
#     print("http://localhost:5000")
#     app.run(host="0.0.0.0", port=5000, debug=True)


import asyncio
import os
import random
import re
import uuid
import threading
from datetime import datetime, timezone

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import phonenumbers
from phonenumbers import geocoder, PhoneNumberFormat, NumberParseException

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoneContact

import csv
from openpyxl import Workbook

# ----------------------- APP CONFIG -----------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "jettool-secret-key-2025"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'jettool.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("static/profile_photos", exist_ok=True)


# ----------------------- DATABASE MODELS -----------------------
class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    target = db.Column(db.String(255))
    status = db.Column(db.String(20), default="running")
    progress = db.Column(db.Integer, default=0)
    current = db.Column(db.String(255), default="Initializing")
    created = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.DateTime, nullable=True)
    logs = db.relationship("TaskLog", backref="task", lazy=True)
    members = db.relationship("Member", backref="task", lazy=True)


class TaskLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey("task.id"))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), default="info")
    message = db.Column(db.Text)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey("task.id"))
    user_id = db.Column(db.BigInteger)
    username = db.Column(db.String(100))
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    country = db.Column(db.String(100))
    premium = db.Column(db.String(10))
    last_seen = db.Column(db.String(50))
    bio = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)


with app.app_context():
    db.create_all()


# ----------------------- TASK MANAGER -----------------------
class TaskManager:
    def __init__(self):
        self.tasks = {}
        self._lock = threading.Lock()
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def create_task(self, target):
        task_id = str(uuid.uuid4())
        with self._lock:
            self.tasks[task_id] = {"full_data": []}
        db_task = Task(id=task_id, target=target)
        db.session.add(db_task)
        db.session.commit()
        self.log(task_id, "Task created", "info")
        return task_id

    def update_progress(self, task_id, progress, msg):
        task = db.session.get(Task, task_id)
        if task:
            task.progress = max(0, min(100, progress))
            task.current = msg
            db.session.commit()
        self.log(task_id, msg, "info")

    def complete(self, task_id):
        task = db.session.get(Task, task_id)
        if task:
            task.status = "completed"
            task.progress = 100
            task.completed = datetime.now(timezone.utc)
            db.session.commit()
            self.log(task_id, "Task completed successfully", "success")

    def fail(self, task_id, msg):
        task = db.session.get(Task, task_id)
        if task:
            task.status = "failed"
            task.progress = 0
            db.session.commit()
            self.log(task_id, msg, "error")

    def log(self, task_id, message, level="info"):
        log = TaskLog(task_id=task_id, message=message, level=level)
        db.session.add(log)
        db.session.commit()


task_manager = TaskManager()


# ----------------------- ROUTES -----------------------
@app.route("/", methods=["GET", "POST"])
def telegram_extractor():
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if not target:
            flash("Target required", "error")
            return redirect(url_for("telegram_extractor"))

        task_id = task_manager.create_task(target)

        options = {
            "include_photos": True,
            "include_names": True,
            "include_premium": True,
            "include_last_seen": True,
            "include_bio": True,
            "add_to_contacts": False,
            "my_group": "",
            "aggressive": True
        }

        asyncio.run_coroutine_threadsafe(
            telegram_member_extractor(target, options, task_id),
            task_manager.loop
        )
        return redirect(url_for("telegram_status", task_id=task_id))

    return render_template("telegram_extractor.html")


@app.route("/task-status/<task_id>")
def task_status_api(task_id):
    task = Task.query.get_or_404(task_id)
    members_count = len(task.members)

    logs = TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.time.desc()).limit(50).all()
    log_list = [{"time": l.time.isoformat(), "level": l.level, "message": l.message} for l in reversed(logs)]

    return jsonify({
        "status": task.status,
        "progress": task.progress,
        "current": task.current,
        "completed": task.completed.isoformat() if task.completed else None,
        "result": {
            "total": members_count,
            "success": task.status == "completed",
            "members": [
                {
                    "user_id": m.user_id,
                    "username": m.username,
                    "full_name": m.full_name,
                    "phone": m.phone,
                    "country": m.country,
                    "premium": m.premium,
                    "last_seen": m.last_seen,
                    "bio": m.bio,
                    "photo_url": m.photo_url
                } for m in task.members
            ],
            "reports": {
                "csv": f"JETTOOL_{task_id[:8]}.csv" if members_count > 0 else None,
                "xlsx": f"JETTOOL_{task_id[:8]}.xlsx" if members_count > 0 else None
            }
        },
        "logs": log_list
    })


@app.route("/status/<task_id>")
def telegram_status(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("telegram_extractor_status.html", task_id=task.id)


@app.route("/view-data/<task_id>")
def view_data(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("view_data.html", members=task.members, task_id=task_id)


@app.route("/reports/<filename>")
def download_report(filename):
    filepath = os.path.join("reports", filename)
    if os.path.exists(filepath):
        return send_from_directory("reports", filename, as_attachment=True)
    return "Report not found", 404


# ----------------------- TELEGRAM EXTRACTION (PERFECT PHONE PARSING) -----------------------
async def telegram_member_extractor(target: str, options: dict, task_id: str):
    api_id = 34339995
    api_hash = "7f73fa5feb68553394202e1e654b545d"
    SAVED_SESSION = "1BJWap1sBu1uT_DRyPhsJRwOxfKF55_JK_GgfAA6lvHW9j2MBvrrM-wM7uiNlItiPd8cJ7cTueoXVwGJ803eMbaWhoQvJl3rVhJ0cteYZ6S-kkshSrel615SgF59Ikgv2hfkJcI63JGV0An3LGfSbV2ZJav0Bk5888OHKotVsvvUjWrKaYu08FVAK4DHMj1Iuv9gtuUvj26FlX52jbvcQzMZ_cCaB4Vd2ZGjMkuA9QRhRbvhQg4Pcr5UZJXeImDrczEXQdb6Bxc68dxwnmsz9U-HCVs4QY2RWD18ktp5hv_smPIV0IhV7-Cn7i_NAmOqj_MQv44HSXbNFsBpvPgvougS3dC8RO3Q="

    client = TelegramClient(StringSession(SAVED_SESSION), api_id, api_hash)

    try:
        await client.start()
        task_manager.update_progress(task_id, 20, "Authenticated successfully")

        entity = await client.get_entity(target)
        entity_title = getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))
        task_manager.update_progress(task_id, 40, f"Target: {entity_title}")

        members = []
        try:
            members = await client.get_participants(entity, limit=0, aggressive=options.get("aggressive", True))
            task_manager.update_progress(task_id, 60, f"Found {len(members)} members directly")
        except:
            task_manager.update_progress(task_id, 60, "Direct fetch failed — scanning message history...")

        if len(members) == 0:
            seen = set()
            async for msg in client.iter_messages(entity, limit=50000):
                if msg.sender_id and msg.sender_id not in seen:
                    try:
                        user = await client.get_entity(msg.sender_id)
                        members.append(user)
                        seen.add(msg.sender_id)
                    except:
                        pass

        total = len(members)
        task_manager.update_progress(task_id, 70, f"Processing {total} members...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("static/profile_photos", exist_ok=True)

        for i, user in enumerate(members):
            if not hasattr(user, 'first_name') or getattr(user, 'bot', False) or getattr(user, 'deleted', False):
                continue

            raw_phone = user.phone or "Hidden"
            formatted_phone = raw_phone
            country = "Unknown"

            if raw_phone != "Hidden" and raw_phone:
                try:
                    # Add + if missing
                    phone_str = "+" + raw_phone if not raw_phone.startswith("+") else raw_phone

                    parsed = phonenumbers.parse(phone_str, None)

                    if phonenumbers.is_valid_number(parsed):
                        formatted_phone = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
                        country_desc = geocoder.description_for_number(parsed, "en")
                        country = country_desc if country_desc else "Unknown"
                    else:
                        # Fallback: try common regions
                        for region in ['NG', 'US', 'GB', 'IN', 'RU', 'BR', 'ID', 'FR', 'DE']:
                            try:
                                parsed = phonenumbers.parse(raw_phone, region)
                                if phonenumbers.is_valid_number(parsed):
                                    formatted_phone = phonenumbers.format_number(parsed,
                                                                                 PhoneNumberFormat.INTERNATIONAL)
                                    country = geocoder.description_for_number(parsed, "en") or region
                                    break
                            except:
                                continue
                except Exception:
                    formatted_phone = raw_phone
                    country = "Parse Failed"

            photo_url = ""
            if options.get("include_photos", True) and getattr(user, 'photo', None):
                try:
                    path = await client.download_profile_photo(
                        user,
                        f"static/profile_photos/{user.id}_{timestamp}.jpg"
                    )
                    if path:
                        photo_url = f"/static/profile_photos/{os.path.basename(path)}"
                except:
                    pass

            member = Member(
                task_id=task_id,
                user_id=user.id,
                username=user.username,
                full_name=f"{user.first_name or ''} {user.last_name or ''}".strip(),
                phone=formatted_phone,
                country=country,
                premium="Yes" if getattr(user, "premium", False) else "No",
                last_seen="Online" if "Online" in str(user.status or "") else "Hidden",
                bio=getattr(user, "about", "") or "",
                photo_url=photo_url
            )
            db.session.add(member)

            if (i + 1) % 20 == 0:
                db.session.commit()
                task_manager.update_progress(
                    task_id,
                    70 + int(((i + 1) / total) * 25),
                    f"Processed {i + 1}/{total}"
                )

        db.session.commit()

        # Generate Reports
        safe_title = re.sub(r'\W+', '_', entity_title)[:30]
        base_name = f"JETTOOL_{safe_title}_{timestamp}"

        if total > 0:
            members_data = Member.query.filter_by(task_id=task_id).all()
            df = pd.DataFrame([{
                "User ID": m.user_id,
                "Username": m.username,
                "Full Name": m.full_name,
                "Phone": m.phone,
                "Country": m.country,
                "Premium": m.premium,
                "Last Seen": m.last_seen,
                "Bio": m.bio
            } for m in members_data])

            csv_path = os.path.join("reports", f"{base_name}.csv")
            xlsx_path = os.path.join("reports", f"{base_name}.xlsx")
            df.to_csv(csv_path, index=False)
            df.to_excel(xlsx_path, index=False)

        task_manager.complete(task_id)

    except Exception as e:
        task_manager.fail(task_id, f"Error: {str(e)}")
    finally:
        if client.is_connected():
            await client.disconnect()


# ----------------------- RUN APP -----------------------
if __name__ == "__main__":
    print("JETTOOL WEB PRO v2025")
    print("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)