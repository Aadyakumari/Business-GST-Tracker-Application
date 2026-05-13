// const express = require('express');
// const cors = require('cors');
// require('dotenv').config();

// //  Import routes
// const authRoutes = require('./routes/authRoutes');

// const app = express();

// //  Middleware
// app.use(cors());
// app.use(express.json());

// //  Routes
// app.use('/api/auth', authRoutes);

// //  Test route
// app.get('/', (req, res) => {
//   res.json({ message: 'GST Tracker API is running ✅' });
// });

// //  Server start
// const PORT = process.env.PORT || 5000;

// app.listen(PORT, () => {
//   console.log(`✅ Server running on http://localhost:${PORT}`);
// });


// const express = require('express');
// const cors = require('cors');
// require('dotenv').config();

// // Import routes
// const authRoutes = require('./routes/authRoutes');

// const app = express();

// // Middleware
// app.use(cors({ origin: process.env.CLIENT_URL || '*' }));
// app.use(express.json());

// // Routes
// app.use('/api/auth', authRoutes);

// // Test route
// app.get('/', (req, res) => {
//   res.json({ message: 'GST Tracker API is running ✅' });
// });

// // 404 Handler
// app.use((req, res) => {
//   res.status(404).json({ message: 'Route not found' });
// });

// // Global Error Handler
// app.use((err, req, res, next) => {
//   console.error(err.stack);
//   res.status(err.status || 500).json({
//     message: err.message || 'Internal Server Error',
//   });
// });

// // Server start
// const PORT = process.env.PORT || 5000;

// app.listen(PORT, () => {
//   console.log(`✅ Server running on http://localhost:${PORT}`);
// });


const express = require('express');
const cors = require('cors');
require('dotenv').config();

// Import routes
const authRoutes = require('./routes/authRoutes');
const invoiceRoutes = require('./routes/invoiceRoutes'); // ← ADDED
const ocrRoutes = require('./routes/ocrRoutes');

const app = express();

// Middleware
app.use(cors({ origin: process.env.CLIENT_URL || '*' }));
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/invoices', invoiceRoutes); // ← ADDED
app.use('/api/ocr', ocrRoutes); // ← ADDED
// Test route
app.get('/', (req, res) => {
  res.json({ message: 'GST Tracker API is running ✅' });
});

// 404 Handler
app.use((req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

// Global Error Handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    message: err.message || 'Internal Server Error',
  });
});

// Server start
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});