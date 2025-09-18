# 2025 Fall ECE Senior Design Miniproject  
**Pico Light Orchestra Instrument**

---

## 📌 Project Definition
This miniproject uses the **Raspberry Pi Pico 2WH SC1634** (wireless, with header pins) to create a light-controlled musical instrument. A photoresistor measures light intensity, and the Pico maps this input to frequencies that drive a piezo buzzer. The result is an interactive system where light changes produce sound, and specific light peaks trigger a **Wii melody** playback.

Students program the Pico using **MicroPython** with **Thonny IDE** (or other IDEs such as VS Code or rshell).  

---

## 🛠️ Hardware
- **Raspberry Pi Pico WH SC1634** (WiFi + Bluetooth, with header pins)  
- **Freenove Pico breakout board FNK0081**  
- **Piezo Buzzer** (SameSky CPT-3095C-300)  
- **10kΩ resistor**  
- **Photoresistor**  

### 🔆 Photoresistor Circuit
- **10kΩ resistor**: from `3V3` → `ADC2` (GP28).  
- **Photoresistor**: from `ADC2` → `AGND`.  
- Polarity is not important.  
- ADC value read in MicroPython:  
  ```python
  photo_sensor_pin = machine.ADC(28)  # GP28 = ADC2

This was prepared by **Team 9/Dynamix II**:  
- Melissa Regalado
- Alexander Hack
- Daniel Gergeus
- Eugene Seoh
- Cynthia Young


