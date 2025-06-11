# ADAS Route Simulator

A Streamlit app for interactive route planning and ADAS (Advanced Driver Assistance Systems) feature simulation.  
Visualize vehicle movement and ADAS segments on a dynamic map using OpenStreetMap and OSRM.

---

## Features

- **Interactive UI:** Enter source, destination, and autonomous level.
- **Route Calculation:** Uses OSRM demo server for routing.
- **Map Visualization:** Folium-based map with colored route segments for different ADAS features.
- **Vehicle Simulation:** Simulate vehicle movement along the route at adjustable speeds (in kmph).
- **Dynamic ADAS Messages:** See enable/disable ADAS notifications as the vehicle moves.
- **Intersection & Road Type Analysis:** Extracts and classifies intersections and road types using OSMnx.

---

## Demo

![ADAS Route Simulator Screenshot](screenshot.png) <!-- Add a screenshot if available -->

---

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/your-username/adas-route-simulator.git
cd adas-route-simulator
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Run the app

```sh
streamlit run streamlit_ui.py
```

---

## Deployment

You can deploy this app for free using [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push your code to GitHub.
2. Go to Streamlit Cloud and connect your repo.
3. Set the main file to `streamlit_ui.py` and deploy!

---

## Project Structure

```
├── streamlit_ui.py
├── routeprocessing.py
├── add_adas_markers.py
├── adas_features.py
├── requirements.txt
└── README.md
```

---

## Dependencies

- streamlit
- folium
- streamlit-folium
- geopy
- requests
- pandas
- osmnx

(See `requirements.txt` for the full list.)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Acknowledgments

- [OpenStreetMap](https://www.openstreetmap.org/)
- [OSRM](http://project-osrm.org/)
- [Streamlit](https://streamlit.io/)
- [Folium](https://python-visualization.github.io/folium/)
- [OSMnx](https://osmnx.readthedocs.io/)

---

*Created for ADAS route simulation and visualization.*