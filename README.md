# Hardhat App Hackathon

A real-time hardhat detection application built for the SkillsProject × Raise Hackathon. This project uses a **YOLOv8 object detection model** to identify whether construction workers are wearing safety helmets.

Model used: [YOLOv8m Hard Hat Detection](https://huggingface.co/keremberke/yolov8m-hard-hat-detection) via Ultralytics.

## Table of Contents

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Demo](#demo)  
- [Installation](#installation)  
  - [Backend (FastAPI)](#backend-fastapi)  
  - [Frontend (Next.js)](#frontend-nextjs)  
- [Usage](#usage)  
- [API](#api)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- Detects hard hats in uploaded images or via camera feed.  
- Returns bounding boxes and classification results.  
- FastAPI backend serving the detection model.  
- Next.js frontend for intuitive user interface.  
- Support for multiple image formats (JPEG, PNG, WebP).  

---

## Tech Stack

- **Frontend:** Next.js, React, Tailwind CSS  
- **Backend:** FastAPI, Python 3.10+  
- **ML Model:** YOLOv8 (Ultralytics)  
- **Deployment:** Hugging Face Hub (for model), Docker-ready  

---

## Installation

### Backend (FastAPI)

Install uv by Astral: https://docs.astral.sh/uv/getting-started/installation/

install dependencies and run the backend with:

```bash
uv run fastapi dev
```

The backend will be available at http://localhost:8000.

---

### Frontend (Next.js)

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install dependencies:

```bash
npm install
```


Start the development server:

```bash
npm run dev
```


The frontend will be available at http://localhost:3000.
