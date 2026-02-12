import { NextRequest, NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";

// Pastikan .env terbaca
loadEnv({ path: path.resolve(process.cwd(), ".env") });

// Use Node.js runtime to support nodemailer and other Node.js modules
export const runtime = 'nodejs';

/**
 * Demo Request API endpoint untuk mengirim email via SMTP
 * POST body: { nama: string, email: string, perusahaan?: string, timestamp?: string, language?: string }
 * Response: { success: boolean, message?: string, error?: string }
 * 
 * SMTP Configuration:
 * Username: demo@baganatech.com
 * Password: (dari environment variable SMTP_PASSWORD)
 * Outgoing Server: mail.baganatech.com
 * SMTP Port: 465
 */

// Dynamic import untuk nodemailer (ESM compatible)
let nodemailer: any;
try {
  nodemailer = require("nodemailer");
} catch (error) {
  console.error("nodemailer tidak ditemukan. Install dengan: npm install nodemailer @types/nodemailer");
}

export async function POST(request: NextRequest) {
  try {
    // Validasi nodemailer
    if (!nodemailer) {
      return NextResponse.json(
        { 
          success: false, 
          error: "Email service tidak tersedia. Silakan hubungi administrator." 
        },
        { 
          status: 503,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Parse request body dengan error handling
    let body;
    try {
      body = await request.json();
    } catch (parseError) {
      console.error("Error parsing request body:", parseError);
      return NextResponse.json(
        { 
          success: false, 
          error: "Format data tidak valid. Pastikan data dikirim sebagai JSON." 
        },
        { 
          status: 400,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }
    
    const { nama, email, perusahaan, timestamp, language } = body;

    // Validasi required fields
    if (!nama || !email) {
      return NextResponse.json(
        { 
          success: false, 
          error: "Nama dan email wajib diisi." 
        },
        { 
          status: 400,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Validasi email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { 
          success: false, 
          error: "Format email tidak valid." 
        },
        { 
          status: 400,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Konfigurasi SMTP dari environment variables
    const smtpHost = process.env.SMTP_HOST || "mail.baganatech.com";
    const smtpPort = parseInt(process.env.SMTP_PORT || "465", 10);
    const smtpUser = process.env.SMTP_USER || "demo@baganatech.com";
    const smtpPassword = process.env.SMTP_PASSWORD;
    const smtpSecure = process.env.SMTP_SECURE !== "false"; // Default true untuk port 465

    // Validasi password SMTP
    if (!smtpPassword) {
      console.error("SMTP_PASSWORD tidak dikonfigurasi di environment variables");
      return NextResponse.json(
        { 
          success: false, 
          error: "Konfigurasi email server tidak lengkap. Silakan hubungi administrator." 
        },
        { 
          status: 500,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Email tujuan (bisa dikonfigurasi via env atau default)
    const recipientEmail = process.env.DEMO_REQUEST_RECIPIENT || "sales@bagana.ai";

    // Buat transporter SMTP
    const transporter = nodemailer.createTransport({
      host: smtpHost,
      port: smtpPort,
      secure: smtpSecure, // true untuk port 465, false untuk port lainnya
      auth: {
        user: smtpUser,
        pass: smtpPassword,
      },
      // Tambahan konfigurasi untuk kompatibilitas
      tls: {
        rejectUnauthorized: process.env.SMTP_REJECT_UNAUTHORIZED !== "false", // Default true untuk production
      },
    });

    // Verifikasi koneksi SMTP dengan error handling
    try {
      await transporter.verify();
      console.log("SMTP connection verified successfully");
    } catch (verifyError: any) {
      console.error("SMTP verification failed:", verifyError);
      return NextResponse.json(
        {
          success: false,
          error: verifyError.code === "EAUTH" 
            ? "Gagal mengautentikasi ke server email. Silakan hubungi administrator."
            : "Gagal terhubung ke server email. Silakan hubungi administrator.",
        },
        { 
          status: 500,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Siapkan konten email berdasarkan bahasa
    const isEnglish = language === "en";
    const emailSubject = isEnglish
      ? `New Demo Request from ${nama}`
      : `Request Demo Baru dari ${nama}`;

    const emailBody = isEnglish
      ? `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #0f766e;">New Demo Request</h2>
          <p>You have received a new demo request from the BAGANA AI landing page.</p>
          
          <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #14b8a6; margin-top: 0;">Request Details:</h3>
            <p><strong>Name:</strong> ${nama}</p>
            <p><strong>Email:</strong> ${email}</p>
            ${perusahaan ? `<p><strong>Company:</strong> ${perusahaan}</p>` : ""}
            ${timestamp ? `<p><strong>Submitted:</strong> ${new Date(timestamp).toLocaleString()}</p>` : ""}
            <p><strong>Language:</strong> ${language === "en" ? "English" : "Indonesian"}</p>
          </div>
          
          <p style="color: #666; font-size: 14px;">
            Please contact this prospect within 1-2 business days to schedule a demo.
          </p>
          
          <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
          <p style="color: #999; font-size: 12px;">
            This email was sent automatically from the BAGANA AI landing page demo request form.
          </p>
        </div>
      `
      : `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #0f766e;">Request Demo Baru</h2>
          <p>Anda menerima request demo baru dari landing page BAGANA AI.</p>
          
          <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #14b8a6; margin-top: 0;">Detail Request:</h3>
            <p><strong>Nama:</strong> ${nama}</p>
            <p><strong>Email:</strong> ${email}</p>
            ${perusahaan ? `<p><strong>Perusahaan:</strong> ${perusahaan}</p>` : ""}
            ${timestamp ? `<p><strong>Dikirim:</strong> ${new Date(timestamp).toLocaleString("id-ID")}</p>` : ""}
            <p><strong>Bahasa:</strong> ${language === "en" ? "Inggris" : "Indonesia"}</p>
          </div>
          
          <p style="color: #666; font-size: 14px;">
            Silakan hubungi prospek ini dalam 1-2 hari kerja untuk menjadwalkan demo.
          </p>
          
          <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
          <p style="color: #999; font-size: 12px;">
            Email ini dikirim otomatis dari form request demo landing page BAGANA AI.
          </p>
        </div>
      `;

    // Kirim email
    const mailOptions = {
      from: `"BAGANA AI Landing Page" <${smtpUser}>`,
      to: recipientEmail,
      subject: emailSubject,
      html: emailBody,
      // Tambahkan reply-to untuk memudahkan reply langsung ke user
      replyTo: email,
    };

    const info = await transporter.sendMail(mailOptions);

    console.log("Email sent successfully:", info.messageId);

    return NextResponse.json(
      {
        success: true,
        message: isEnglish
          ? "Demo request sent successfully. We will contact you within 1-2 business days."
          : "Request demo berhasil dikirim. Tim kami akan menghubungi Anda dalam 1-2 hari kerja.",
        messageId: info.messageId,
      },
      { 
        status: 200,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        }
      }
    );
  } catch (error: any) {
    console.error("Error sending demo request email:", error);
    console.error("Error stack:", error.stack);
    console.error("Error code:", error.code);
    console.error("Error response:", error.response);

    // Handle specific SMTP errors
    if (error.code === "EAUTH" || error.code === "ECONNECTION") {
      return NextResponse.json(
        {
          success: false,
          error: "Gagal mengautentikasi ke server email. Silakan hubungi administrator.",
        },
        { 
          status: 500,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    // Handle JSON parsing errors
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        {
          success: false,
          error: "Format data tidak valid. Silakan coba lagi.",
        },
        { 
          status: 400,
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
          }
        }
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: error.message || "Terjadi kesalahan saat mengirim email. Silakan coba lagi.",
      },
      { 
        status: 500,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        }
      }
    );
  }
}

// Handle OPTIONS untuk CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
