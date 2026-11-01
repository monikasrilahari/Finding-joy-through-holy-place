from flask import Flask, render_template, jsonify, request
import sqlite3
from pathlib import Path
from datetime import datetime
app=Flask(__name__)
DB_PATH=Path(__file__).resolve().parent/"finding_joy.db"
PLACES=[('Tirumala Venkateswara Temple',
  'Tirupati',
  'Andhra Pradesh',
  'Temple',
  'Hinduism',
  '/static/images/tirumala-venkateswara-temple.jpg',
  "One of India's most visited pilgrimage destinations, dedicated to Lord Venkateswara. Set amid the green "
  'Tirumala hills, the temple is known for its devotional traditions and grand architecture.'),
 ('Kashi Vishwanath Temple',
  'Varanasi',
  'Uttar Pradesh',
  'Temple',
  'Hinduism',
  '/static/images/kashi-vishwanath-temple.jpg',
  'A revered Shiva temple in the ancient city of Varanasi, close to the sacred Ganga. Its spiritual '
  "atmosphere is deeply connected with the city's centuries-old traditions."),
 ('Golden Temple',
  'Amritsar',
  'Punjab',
  'Gurudwara',
  'Sikhism',
  '/static/images/golden-temple.jpg',
  'Sri Harmandir Sahib is the holiest shrine in Sikhism, admired for its golden façade, peaceful sarovar and '
  'the community kitchen that welcomes visitors.'),
 ('Meenakshi Amman Temple',
  'Madurai',
  'Tamil Nadu',
  'Temple',
  'Hinduism',
  '/static/images/meenakshi-amman-temple.jpg',
  'A celebrated historic temple complex known for its colourful sculpted towers, intricate pillars and '
  'vibrant traditions dedicated to Goddess Meenakshi and Lord Sundareswarar.'),
 ('Jagannath Temple',
  'Puri',
  'Odisha',
  'Temple',
  'Hinduism',
  '/static/images/jagannath-temple.jpg',
  'An important Char Dham pilgrimage site dedicated to Lord Jagannath. The annual Rath Yatra draws devotees '
  'and visitors from across India.'),
 ('Somnath Temple',
  'Prabhas Patan',
  'Gujarat',
  'Temple',
  'Hinduism',
  '/static/images/somnath-temple.jpg',
  'A prominent Jyotirlinga shrine on the Arabian Sea coast, known for its striking seaside setting and long '
  'history of devotion and rebuilding.'),
 ('Brihadeeswarar Temple',
  'Thanjavur',
  'Tamil Nadu',
  'Temple',
  'Hinduism',
  '/static/images/brihadeeswarar-temple.jpg',
  'A UNESCO-listed Chola masterpiece celebrated for its monumental vimana, stone craftsmanship and '
  'extraordinary Dravidian architecture.'),
 ('Kedarnath Temple',
  'Kedarnath',
  'Uttarakhand',
  'Temple',
  'Hinduism',
  '/static/images/kedarnath-temple.jpg',
  'A sacred Himalayan shrine dedicated to Lord Shiva, surrounded by dramatic mountain scenery. It is one of '
  'the twelve Jyotirlingas and part of the Char Dham.'),
 ('Vaishno Devi',
  'Katra',
  'Jammu & Kashmir',
  'Temple',
  'Hinduism',
  '/static/images/vaishno-devi.jpg',
  'A major pilgrimage destination in the Trikuta Mountains, reached by a scenic uphill route to the holy '
  'cave shrine of Mata Vaishno Devi.'),
 ('Akshardham Temple',
  'New Delhi',
  'Delhi',
  'Temple',
  'Hinduism',
  '/static/images/akshardham-temple.jpg',
  'A grand cultural and spiritual complex showcasing traditional Indian architecture, craftsmanship, '
  'exhibitions and gardens.'),
 ('Ramanathaswamy Temple',
  'Rameswaram',
  'Tamil Nadu',
  'Temple',
  'Hinduism',
  '/static/images/ramanathaswamy-temple.jpg',
  'A major pilgrimage site famed for its long pillared corridors and sacred wells, associated with the '
  'Ramayana tradition.'),
 ('Siddhivinayak Temple',
  'Mumbai',
  'Maharashtra',
  'Temple',
  'Hinduism',
  '/static/images/siddhivinayak-temple.jpg',
  'A much-loved Mumbai shrine dedicated to Lord Ganesha, visited by people seeking blessings and beginning '
  'new ventures.'),
 ('Haji Ali Dargah',
  'Mumbai',
  'Maharashtra',
  'Mosque',
  'Islam',
  '/static/images/haji-ali-dargah.jpg',
  'A renowned mosque and dargah set on an islet off the Mumbai coast, connected to the shore by a causeway '
  'that is surrounded by the sea at high tide.'),
 ('Jama Masjid',
  'Old Delhi',
  'Delhi',
  'Mosque',
  'Islam',
  '/static/images/jama-masjid.jpg',
  "One of India's largest historic mosques, built in the Mughal era and known for its expansive courtyard, "
  'domes and minarets.'),
 ('Charminar Mosque',
  'Hyderabad',
  'Telangana',
  'Mosque',
  'Islam',
  '/static/images/charminar-mosque.jpg',
  "The iconic Charminar stands at the heart of Hyderabad's old city, reflecting the region's Deccan "
  'heritage, bustling bazaars and Islamic architecture.'),
 ('Basilica of Bom Jesus',
  'Old Goa',
  'Goa',
  'Church',
  'Christianity',
  '/static/images/basilica-of-bom-jesus.jpg',
  'A UNESCO World Heritage church famed for its Baroque architecture and its place in the history of '
  'Christianity in Goa.'),
 ('San Thome Basilica',
  'Chennai',
  'Tamil Nadu',
  'Church',
  'Christianity',
  '/static/images/san-thome-basilica.jpg',
  'A historic neo-Gothic basilica traditionally associated with the resting place of St. Thomas the '
  'Apostle.'),
 ('Velankanni Basilica',
  'Velankanni',
  'Tamil Nadu',
  'Church',
  'Christianity',
  '/static/images/velankanni-basilica.jpg',
  'The Basilica of Our Lady of Good Health is a major Christian pilgrimage centre, welcoming visitors from '
  'many regions and communities.'),
 ('Tawang Monastery',
  'Tawang',
  'Arunachal Pradesh',
  'Buddhist',
  'Buddhism',
  '/static/images/tawang-monastery.jpg',
  'One of the largest Buddhist monasteries in India, set in the Eastern Himalayas and known for its peaceful '
  'courtyards, prayer halls and mountain views.'),
 ('Mahabodhi Temple',
  'Bodh Gaya',
  'Bihar',
  'Buddhist',
  'Buddhism',
  '/static/images/mahabodhi-temple.jpg',
  'A UNESCO World Heritage site marking the place where Siddhartha Gautama is believed to have attained '
  'enlightenment and become the Buddha.')]
def get_db():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with get_db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS places(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,city TEXT,state TEXT,type TEXT,faith TEXT,image TEXT,description TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS favorites(id INTEGER PRIMARY KEY AUTOINCREMENT,place_id INTEGER REFERENCES places(id),visitor_token TEXT DEFAULT 'guest',created_at TEXT,UNIQUE(place_id,visitor_token))")
        c.execute("CREATE TABLE IF NOT EXISTS visit_plans(id INTEGER PRIMARY KEY AUTOINCREMENT,visitor_name TEXT,place_id INTEGER REFERENCES places(id),note TEXT,created_at TEXT)")
        image_map = {
            'Tirumala Venkateswara Temple': '/static/images/tirumala-venkateswara-temple.jpg',
            'Kashi Vishwanath Temple': '/static/images/kashi-vishwanath-temple.jpg',
            'Golden Temple': '/static/images/golden-temple.jpg',
            'Meenakshi Amman Temple': '/static/images/meenakshi-amman-temple.jpg',
            'Jagannath Temple': '/static/images/jagannath-temple.jpg',
            'Somnath Temple': '/static/images/somnath-temple.jpg',
            'Brihadeeswarar Temple': '/static/images/brihadeeswarar-temple.jpg',
            'Kedarnath Temple': '/static/images/kedarnath-temple.jpg',
            'Vaishno Devi': '/static/images/vaishno-devi.jpg',
            'Akshardham Temple': '/static/images/akshardham-temple.jpg',
            'Ramanathaswamy Temple': '/static/images/ramanathaswamy-temple.jpg',
            'Siddhivinayak Temple': '/static/images/siddhivinayak-temple.jpg',
            'Haji Ali Dargah': '/static/images/haji-ali-dargah.jpg',
            'Jama Masjid': '/static/images/jama-masjid.jpg',
            'Charminar Mosque': '/static/images/charminar-mosque.jpg',
            'Basilica of Bom Jesus': '/static/images/basilica-of-bom-jesus.jpg',
            'San Thome Basilica': '/static/images/san-thome-basilica.jpg',
            'Velankanni Basilica': '/static/images/velankanni-basilica.jpg',
            'Tawang Monastery': '/static/images/tawang-monastery.jpg',
            'Mahabodhi Temple': '/static/images/mahabodhi-temple.jpg',
        }
        for place_name, local_image in image_map.items():
            c.execute("UPDATE places SET image=? WHERE name=?", (local_image, place_name))
        if c.execute("SELECT COUNT(*) FROM places").fetchone()[0]==0:
            c.executemany("INSERT INTO places(name,city,state,type,faith,image,description) VALUES(?,?,?,?,?,?,?)",PLACES)
        # Use each downloaded local photo when present; otherwise keep its illustration fallback.
        for place_name, photo_path in image_map.items():
            project_root = Path(__file__).resolve().parent
            jpg_file = project_root / photo_path.lstrip("/")
            png_path = photo_path.rsplit(".", 1)[0] + ".png"
            png_file = project_root / png_path.lstrip("/")
            if jpg_file.exists():
                chosen_path = photo_path
            elif png_file.exists():
                chosen_path = png_path
            else:
                chosen_path = photo_path.rsplit(".", 1)[0] + ".svg"
            c.execute("UPDATE places SET image=? WHERE name=?", (chosen_path, place_name))
@app.route("/")
def home(): return render_template("index.html")
@app.route("/api/health")
def health(): return jsonify(status="ok",database="connected")
@app.route("/api/places")
def places_api():
    with get_db() as c: rows=c.execute("SELECT * FROM places ORDER BY id").fetchall()
    return jsonify([dict(x) for x in rows])
@app.route("/api/favorites",methods=["GET","POST"])
def favorites_api():
    with get_db() as c:
        if request.method=="GET":
            rows=c.execute("SELECT f.place_id,p.name,f.created_at FROM favorites f JOIN places p ON p.id=f.place_id WHERE f.visitor_token='guest' ORDER BY f.id DESC").fetchall()
            return jsonify([dict(x) for x in rows])
        d=request.get_json(silent=True) or {}
        try: pid=int(d.get("place_id"))
        except (TypeError,ValueError): return jsonify(error="Choose a valid place."),400
        if not c.execute("SELECT id FROM places WHERE id=?",(pid,)).fetchone(): return jsonify(error="Place not found."),404
        old=c.execute("SELECT id FROM favorites WHERE place_id=? AND visitor_token='guest'",(pid,)).fetchone()
        if old: c.execute("DELETE FROM favorites WHERE id=?",(old["id"],)); return jsonify(saved=False)
        c.execute("INSERT INTO favorites(place_id,visitor_token,created_at) VALUES(?,?,?)",(pid,"guest",datetime.now().strftime("%Y-%m-%d %H:%M")))
        return jsonify(saved=True)
@app.route("/api/visits",methods=["POST"])
def visits_api():
    d=request.get_json(silent=True) or {}; name=str(d.get("name","")).strip(); note=str(d.get("note","")).strip()
    try: pid=int(d.get("place_id"))
    except (TypeError,ValueError): return jsonify(error="Please choose a destination."),400
    if not name or len(name)>80: return jsonify(error="Enter your name (maximum 80 characters)."),400
    with get_db() as c:
        if not c.execute("SELECT id FROM places WHERE id=?",(pid,)).fetchone(): return jsonify(error="Place not found."),404
        c.execute("INSERT INTO visit_plans(visitor_name,place_id,note,created_at) VALUES(?,?,?,?)",(name,pid,note[:500],datetime.now().strftime("%Y-%m-%d %H:%M")))
    return jsonify(message="Visit idea saved."),201
@app.route("/admin")
def admin():
    with get_db() as c:
        pc=c.execute("SELECT COUNT(*) FROM places").fetchone()[0]; vc=c.execute("SELECT COUNT(*) FROM visit_plans").fetchone()[0]; fc=c.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
        visits=c.execute("SELECT v.visitor_name AS name,p.name AS place_name,v.note,v.created_at FROM visit_plans v JOIN places p ON p.id=v.place_id ORDER BY v.id DESC").fetchall()
        favorites=c.execute("SELECT p.name,f.created_at FROM favorites f JOIN places p ON p.id=f.place_id ORDER BY f.id DESC").fetchall()
    return render_template("admin.html",place_count=pc,visit_count=vc,favorite_count=fc,visits=visits,favorites=favorites)
init_db()
if __name__=="__main__":
    print("Open http://127.0.0.1:5000")
    app.run(debug=True)
