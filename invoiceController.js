
// CREATE INVOICE
// exports.createInvoice = async (req, res) => {
//   try {
//     const { partyName, amount, gstRate, type, description, date } = req.body;

//     // Auto calculate GST
//     const gstAmount = (amount * gstRate) / 100;
//     const totalAmount = amount + gstAmount;

//     const invoice = await prisma.invoice.create({
//       data: {
//         userId: req.user.id,
//         partyName,
//         amount,
//         gstRate,
//         gstAmount,
//         totalAmount,
//         type,        // "SALE" or "PURCHASE"
//         description,
//         date: date ? new Date(date) : new Date()
//       }
//     });

//     res.json({ message: 'Invoice created!', invoice });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };

// // GET ALL INVOICES
// exports.getInvoices = async (req, res) => {
//   try {
//     const invoices = await prisma.invoice.findMany({
//       where: { userId: req.user.id },
//       orderBy: { date: 'desc' }
//     });

//     res.json({ invoices });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };

// // DELETE INVOICE
// exports.deleteInvoice = async (req, res) => {
//   try {
//     const { id } = req.params;

//     await prisma.invoice.delete({
//       where: { id: parseInt(id) }
//     });

//     res.json({ message: 'Invoice deleted!' });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };
// // DASHBOARD SUMMARY
// exports.getDashboard = async (req, res) => {
//   try {
//     const invoices = await prisma.invoice.findMany({
//       where: { userId: req.user.id }
//     });

//     const sales = invoices.filter(i => i.type === 'SALE');
//     const purchases = invoices.filter(i => i.type === 'PURCHASE');

//     const totalSales = sales.reduce((sum, i) => sum + i.amount, 0);
//     const totalPurchases = purchases.reduce((sum, i) => sum + i.amount, 0);

//     const gstCollected = sales.reduce((sum, i) => sum + i.gstAmount, 0);
//     const gstPaid = purchases.reduce((sum, i) => sum + i.gstAmount, 0);

//     const gstPayable = gstCollected - gstPaid; // final GST to pay govt

//     res.json({
//       totalSales,
//       totalPurchases,
//       gstCollected,
//       gstPaid,
//       gstPayable,
//       totalInvoices: invoices.length
//     });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };


// // ─── CREATE INVOICE ───────────────────────────────────────────────────────────
// exports.createInvoice = async (req, res) => {
//   try {
//     const {
//       partyName, amount, gstRate, type,
//       description, date, sellerState, buyerState,
//     } = req.body;

//     const gstAmount   = (amount * gstRate) / 100;
//     const totalAmount = amount + gstAmount;

//     let cgst = 0, sgst = 0, igst = 0;
//     let transactionType = 'intra';

//     const seller = sellerState || 'Maharashtra';
//     const buyer  = buyerState  || 'Maharashtra';

//     if (seller === buyer) {
//       cgst = gstAmount / 2;
//       sgst = gstAmount / 2;
//       transactionType = 'intra';
//     } else {
//       igst = gstAmount;
//       transactionType = 'inter';
//     }

//     const invoice = await prisma.invoice.create({
//       data: {
//         userId: req.user.id,
//         partyName, amount, gstRate, gstAmount,
//         cgst, sgst, igst, totalAmount, type,
//         transactionType, sellerState: seller, buyerState: buyer,
//         description,
//         date: date ? new Date(date) : new Date(),
//       },
//     });

//     res.status(201).json({ message: 'Invoice created!', invoice });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };

// // ─── GET ALL INVOICES ─────────────────────────────────────────────────────────
// exports.getInvoices = async (req, res) => {
//   try {
//     const invoices = await prisma.invoice.findMany({
//       where: { userId: req.user.id },
//       orderBy: { date: 'desc' },
//     });
//     res.json({ invoices });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };

// // ─── DELETE INVOICE ───────────────────────────────────────────────────────────
// exports.deleteInvoice = async (req, res) => {
//   try {
//     const existing = await prisma.invoice.findFirst({
//       where: { id: req.params.id, userId: req.user.id },
//     });

//     if (!existing) return res.status(404).json({ message: 'Invoice not found' });

//     await prisma.invoice.delete({ where: { id: req.params.id } });
//     res.json({ message: 'Invoice deleted successfully' });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };

// // ─── GET DASHBOARD ────────────────────────────────────────────────────────────
// exports.getDashboard = async (req, res) => {
//   try {
//     const userId = req.user.id;

//     const [invoices, totals] = await Promise.all([
//       prisma.invoice.findMany({
//         where: { userId },
//         orderBy: { date: 'desc' },
//         take: 5,
//       }),
//       prisma.invoice.aggregate({
//         where: { userId },
//         _count: { id: true },
//         _sum: {
//           amount: true, gstAmount: true, totalAmount: true,
//           cgst: true, sgst: true, igst: true,
//         },
//       }),
//     ]);

//     const [intraStats, interStats] = await Promise.all([
//       prisma.invoice.aggregate({
//         where: { userId, transactionType: 'intra' },
//         _count: { id: true },
//         _sum: { cgst: true, sgst: true, totalAmount: true },
//       }),
//       prisma.invoice.aggregate({
//         where: { userId, transactionType: 'inter' },
//         _count: { id: true },
//         _sum: { igst: true, totalAmount: true },
//       }),
//     ]);

//     res.json({
//       summary: {
//         totalInvoices: totals._count.id,
//         totalAmount:   totals._sum.amount      || 0,
//         totalGst:      totals._sum.gstAmount   || 0,
//         totalBilled:   totals._sum.totalAmount || 0,
//         totalCgst:     totals._sum.cgst        || 0,
//         totalSgst:     totals._sum.sgst        || 0,
//         totalIgst:     totals._sum.igst        || 0,
//       },
//       intraState: {
//         count:       intraStats._count.id,
//         totalCgst:   intraStats._sum.cgst        || 0,
//         totalSgst:   intraStats._sum.sgst        || 0,
//         totalBilled: intraStats._sum.totalAmount || 0,
//       },
//       interState: {
//         count:       interStats._count.id,
//         totalIgst:   interStats._sum.igst        || 0,
//         totalBilled: interStats._sum.totalAmount || 0,
//       },
//       recentInvoices: invoices,
//     });
//   } catch (err) {
//     res.status(500).json({ message: 'Server error', error: err.message });
//   }
// };











const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// CREATE INVOICE
exports.createInvoice = async (req, res) => {
  try {
    const { partyName, amount, gstRate, type, description, date, sellerState, buyerState } = req.body;

    const gstAmount = (amount * gstRate) / 100;
    const totalAmount = amount + gstAmount;

    const seller = sellerState || 'Maharashtra';
    const buyer = buyerState || 'Maharashtra';

    let cgst = 0, sgst = 0, igst = 0, transactionType = 'intra';

    if (seller === buyer) {
      cgst = gstAmount / 2;
      sgst = gstAmount / 2;
      transactionType = 'intra';
    } else {
      igst = gstAmount;
      transactionType = 'inter';
    }

    const invoice = await prisma.invoice.create({
      data: {
        userId: req.user.id,
        partyName,
        amount,
        gstRate,
        gstAmount,
        cgst,
        sgst,
        igst,
        totalAmount,
        type,
        transactionType,
        sellerState: seller,
        buyerState: buyer,
        description,
        date: date ? new Date(date) : new Date()
      }
    });

    res.json({ message: 'Invoice created!', invoice });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

// GET ALL INVOICES
exports.getInvoices = async (req, res) => {
  try {
    const invoices = await prisma.invoice.findMany({
      where: { userId: req.user.id },
      orderBy: { date: 'desc' }
    });
    res.json({ invoices });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

// DELETE INVOICE
exports.deleteInvoice = async (req, res) => {
  try {
    const { id } = req.params;
    await prisma.invoice.delete({
      where: { id: parseInt(id) }
    });
    res.json({ message: 'Invoice deleted!' });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

// DASHBOARD SUMMARY
exports.getDashboard = async (req, res) => {
  try {
    const invoices = await prisma.invoice.findMany({
      where: { userId: req.user.id }
    });

    const sales = invoices.filter(i => i.type === 'SALE');
    const purchases = invoices.filter(i => i.type === 'PURCHASE');

    const totalSales = sales.reduce((sum, i) => sum + i.amount, 0);
    const totalPurchases = purchases.reduce((sum, i) => sum + i.amount, 0);
    const gstCollected = sales.reduce((sum, i) => sum + i.gstAmount, 0);
    const gstPaid = purchases.reduce((sum, i) => sum + i.gstAmount, 0);
    const gstPayable = gstCollected - gstPaid;

    const totalCGST = invoices.reduce((sum, i) => sum + (i.cgst || 0), 0);
    const totalSGST = invoices.reduce((sum, i) => sum + (i.sgst || 0), 0);
    const totalIGST = invoices.reduce((sum, i) => sum + (i.igst || 0), 0);

    res.json({
      totalSales,
      totalPurchases,
      gstCollected,
      gstPaid,
      gstPayable,
      totalInvoices: invoices.length,
      totalCGST,
      totalSGST,
      totalIGST
    });
  } catch (err) {
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};