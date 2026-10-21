# Docker Guide - Chilli Plant Detection System

මෙම project එක වෙනත් ඕනෑම පරිගණකයක (Laptop / PC) Python, PyTorch, හෝ dependencies install නොකර **Docker** මඟින් පහසුවෙන්ම run කරගත හැක.

---

## 1. වෙනත් Laptop එකකට ගෙන යාම (Transfer to another laptop)

ඔබට පහත ක්‍රම දෙකෙන් එකක් තෝරාගත හැක:
- **ක්‍රමය A:** [`Chilli_Plant_Detection_System.zip`](file:///c:/Users/lithi/Downloads/Lithira_Ai_part/Lithira_Ai_part/Chilli_Plant_Detection_System.zip) file එක Pen drive එකකට copy කර අලුත් laptop එකට දමා Extract කරන්න.
- **ක්‍රමය B:** සම්පූර්ණ [`Chilli_Plant_Detection_System`](file:///c:/Users/lithi/Downloads/Lithira_Ai_part/Lithira_Ai_part/Chilli_Plant_Detection_System) folder එකම copy කරගෙන යන්න. (Trained YOLO model `best.pt` file එකද `backend/model/best.pt` තුළ ඇතුළත් කර ඇත).

---

## 2. අවශ්‍ය වන දේ (Prerequisites)

- අලුත් laptop එකේ **Docker Desktop** install කර තිබිය යුතුය.
  - [Docker Desktop බාගත කරගැනීමට](https://www.docker.com/products/docker-desktop/)
- Docker Desktop open කර running තත්ත්වයේ තබන්න.

---

## 3. Docker මඟින් Run කිරීම (How to Run)

### ක්‍රමය 1: One-Click Launcher (වඩාත්ම පහසුයි)
`Chilli_Plant_Detection_System` folder එක තුළ ඇති **`docker-run.bat`** file එක double-click කරන්න.
- එය ස්වයංක්‍රීයව backend container එක build කර start කරයි.
- විනාඩි කිහිපයකින් ඔබගේ browser එකෙන් Swagger API Docs `http://localhost:8000/docs` විවෘත වේ.

### ක්‍රමය 2: Terminal / Command Prompt හරහා
`Chilli_Plant_Detection_System` folder එක තුළ Terminal එකක් open කර:

```bash
docker compose up --build -d
```

---

## 4. පද්ධතියට පිවිසීම (Access URLs)

- **Backend API (FastAPI):** [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Docker Stop කිරීම (Stop Containers)

- `docker-stop.bat` double-click කරන්න.
- හෝ Terminal එකේ:
  ```bash
  docker compose down
  ```
