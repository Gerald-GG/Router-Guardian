# 🚀 Router Guardian

**Router Guardian** is a full-stack network management tool that allows you to:

- 🖥️ **Scan and list connected devices** on your router
- 🔒 **Block or unblock devices** for specified durations
- ⏱️ **Auto-refresh device status**
- 🌙 **Toggle dark mode**
- 📱 **Responsive UI** for mobile, tablet, and laptop views

---

## 📂 **Project Structure**

Router-Guardian/
├── backend/
│ ├── app.py
│ ├── api/
│ ├── data/
│ ├── router_control/
│ ├── scanner/
│ ├── utils/
│ └── device_tracking.json
├── frontend/
│ ├── src/
│ │ ├── App.jsx
│ │ ├── main.jsx
│ │ └── index.css
│ ├── public/
│ ├── package.json
│ ├── vite.config.js
│ └── ...
└── README.md

---

## ⚙️ **Backend**

### 🐍 **Built With**

- **Python 3**
- **Flask** for REST APIs
- **Custom router control logic** (Huawei routers by default)

### 🔧 **Endpoints**

- `GET /devices` — List all connected devices
- `POST /block` — Block a device by MAC address for a specified duration
- `POST /unblock` — Unblock a device
- `GET /wifi` — Get current SSID

### ▶ **Running the Backend**

```bash
# Navigate to backend folder
cd backend

# (Optional) Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run Flask app
python3 app.py
💻 Frontend
🛠️ Built With
React.js with Vite

Tailwind CSS for utility-first responsive styling

✨ Features
Paginated device table with sorting and search

Block/unblock buttons with status badges

Auto-refresh toggle

Dark mode toggle

View mode switch (mobile, tablet, laptop emulation)

▶ Running the Frontend
bash
Copy
Edit
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
The frontend runs on http://localhost:5173 and interacts with the backend at http://localhost:5000.

📸 Screenshots
Light Mode	Dark Mode

⚠️ Add actual screenshots in the /screenshots folder and update these paths.

🔒 Security & Considerations
✅ Uses local device scanning and router login logic
✅ Only accessible on your local network (unless deployed securely)
⚠️ Do not expose the backend API to the public internet without authentication and rate limiting

📝 Future Enhancements
Scheduler for auto block/unblock routines

User authentication for admin actions

Multi-router support

Export device data as CSV or JSON

👤 Author
Gerald Mwangi

💻 Linux (Parrot OS) user

🌐 Based in Kenya

🤝 Contributing
Contributions, issues, and feature requests are welcome!
Open an issue or submit a pull request to improve Router Guardian.

📄 License
This project is licensed under the MIT License.

