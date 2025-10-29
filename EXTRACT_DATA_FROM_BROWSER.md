# How to Extract Data from Forio Web Interface

Since the graphs show the data you need, we can extract it from the browser.

---

## 🔍 Method 1: Check for Export Feature

**When viewing a run with graphs:**

1. Look for any of these:
   - "Export Data" button
   - "Download" button
   - "Save as CSV/JSON"
   - Three-dot menu (⋮)
   - Settings icon (⚙️)

2. If found, export one run and check the format

---

## 🔧 Method 2: Browser Developer Tools

**The graphs are loading data from somewhere. Let's find it:**

### Step 1: Open Developer Tools

1. Log into Forio as MIT@2025002
2. Open a run that shows graphs
3. Press `F12` or `Cmd+Option+I` (Mac) to open DevTools
4. Go to the **Network** tab

### Step 2: Reload and Capture

1. With Network tab open, refresh the page
2. Look for API calls in the network log
3. Filter by:
   - XHR (AJAX requests)
   - Fetch
   - Look for URLs containing "variable", "data", "result"

### Step 3: Find the Data

Look for responses that contain:
- Arrays of numbers (time series data)
- Variable names like "compromised_systems", "profit", etc.
- JSON with the graph data

### Step 4: Copy the Request

Once you find the right API call:
1. Right-click on it
2. "Copy as cURL" or "Copy as fetch"
3. Share it with me - I can convert it to Python

---

## 🎯 Method 3: Console Extraction

**If the data is in JavaScript variables:**

### Step 1: Open Console

1. While viewing the graphs, press `F12`
2. Go to **Console** tab

### Step 2: Try These Commands

```javascript
// Try to find the data in common places
console.log(window.runData);
console.log(window.chartData);
console.log(window.variables);

// Or search all window properties
for (let key in window) {
    if (key.toLowerCase().includes('data') || 
        key.toLowerCase().includes('chart') ||
        key.toLowerCase().includes('variable')) {
        console.log(key, window[key]);
    }
}
```

### Step 3: Export What You Find

If you find the data:
```javascript
// Copy it to clipboard
copy(window.runData); // or whatever variable has the data
```

Then paste it and share with me.

---

## 📊 Method 4: Inspect the Chart

**If using Chart.js or similar:**

### In Console, try:

```javascript
// Get all canvas elements (charts)
let charts = document.querySelectorAll('canvas');

// Try to access Chart.js instances
if (window.Chart && Chart.instances) {
    Chart.instances.forEach((chart, i) => {
        console.log(`Chart ${i}:`, chart.data);
    });
}

// Or try this
let chartElements = document.querySelectorAll('canvas');
chartElements.forEach((canvas, i) => {
    if (canvas.chart) {
        console.log(`Chart ${i} data:`, canvas.chart.data);
    }
});
```

---

## 🎯 What I Need From You

**Please try the methods above and tell me:**

1. **Is there an export button?**
   - If yes: Export one run and share the file

2. **What API calls do you see in Network tab?**
   - URLs that fetch the graph data
   - I can replicate them in Python

3. **Can you extract data from console?**
   - Any JavaScript variables containing the data

4. **What format is the data in?**
   - JSON? CSV? Arrays?

---

## 💡 Why This Matters

Once we know how the web interface gets the data, we can:
- ✅ Replicate the same API calls in Python
- ✅ Automatically fetch data for all runs
- ✅ No manual entry needed
- ✅ Dashboard works with real data

---

## 🚀 Quick Win Option

**If you can't find the technical details:**

Just manually record the data you see in the graphs for 2-3 runs:
```bash
python manual_data_entry.py
```

Enter:
- Compromised systems (final value or average)
- Profit (final value)
- Resource allocation (prevention, detection, response budgets)

This gets your dashboard working with real data **immediately** while we figure out the automated approach.

---

## 📞 Next Steps

1. Check for export button (30 seconds)
2. If no export, open DevTools Network tab (2 minutes)
3. Share what you find
4. I'll write the extraction code

**Or just do manual entry for now and we'll automate later!**
