const Tesseract = require('tesseract.js');
const fs = require('fs');

exports.scanInvoice = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No image uploaded' });
    }

    const imagePath = req.file.path;

    const { data: { text } } = await Tesseract.recognize(imagePath, 'eng', {
      logger: m => console.log(m)
    });

    console.log('OCR Text:', text);

    const extracted = extractInvoiceData(text);

    fs.unlinkSync(imagePath);

    res.json({
      success: true,
      rawText: text,
      extracted
    });

  } catch (err) {
    res.status(500).json({ message: 'OCR failed', error: err.message });
  }
};

function extractInvoiceData(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(l => l);

  let amount = 0;
  let gstRate = 18;
  let partyName = '';
  let description = '';

  for (const line of lines) {
    const lower = line.toLowerCase();

    if (lower.includes('total') || lower.includes('amount') || lower.includes('rs') || lower.includes('₹')) {
      const numbers = line.match(/[\d,]+\.?\d*/g);
      if (numbers) {
        const num = parseFloat(numbers[numbers.length - 1].replace(',', ''));
        if (num > amount && num < 10000000) amount = num;
      }
    }

    if (lower.includes('gst') || lower.includes('tax')) {
      const rates = line.match(/\d+%?/g);
      if (rates) {
        const rate = parseInt(rates[0]);
        if ([5, 12, 18, 28].includes(rate)) gstRate = rate;
      }
    }

    if (!partyName && line.length > 3 && line.length < 50 &&
        !lower.includes('invoice') && !lower.includes('date') &&
        !lower.includes('total') && isNaN(line[0])) {
      partyName = line;
    }

    if (lower.includes('item') || lower.includes('product') ||
        lower.includes('service') || lower.includes('description')) {
      description = line.replace(/item|product|service|description/gi, '').trim();
    }
  }

  return { partyName, amount, gstRate, description };
}