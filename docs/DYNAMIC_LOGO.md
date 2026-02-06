# Dynamic Logo Configuration

## Overview

Logo di header telah diubah menjadi dinamis dan dapat dikonfigurasi dengan mudah melalui file konfigurasi. Logo dapat diposisikan di pojok kiri (default), tengah, atau pojok kanan header secara dinamis.

## Struktur

### File Konfigurasi
- **`lib/logo-config.ts`**: File konfigurasi utama untuk logo
  - `LOGO_CONFIG`: Objek konfigurasi logo default
  - `getLogoConfig()`: Fungsi untuk mendapatkan konfigurasi logo saat ini
  - `updateLogoConfig(config)`: Fungsi untuk mengupdate konfigurasi logo
  - Helper functions: `setLogoPath()`, `setLogoText()`, `setLogoHref()`, `setLogoPosition()`, dll.

### Komponen
- **`components/Logo.tsx`**: Komponen logo yang mendukung mode dinamis
  - Props `dynamic`: Aktifkan mode dinamis (default: false)
  - Props manual masih didukung untuk override
  - Otomatis menggunakan konfigurasi default jika tidak ada props

- **`components/PageLayout.tsx`**: Layout wrapper dengan logo dinamis
  - Props `dynamicLogo`: Aktifkan logo dinamis (default: true)
  - Otomatis mengatur layout header berdasarkan posisi logo (left/center/right)

### Hook
- **`lib/hooks/useLogo.ts`**: React hook untuk logo dinamis
  - Dapat diperluas untuk fetch dari API di masa depan
  - Support auto-refresh

## Penggunaan

### Menggunakan Logo Dinamis (Default)

```tsx
import { PageLayout } from "@/components/PageLayout";

export default function MyPage() {
  return (
    <PageLayout currentPath="/dashboard" dynamicLogo={true}>
      {/* Content */}
    </PageLayout>
  );
}
```

### Menggunakan Logo Manual

```tsx
import { Logo } from "@/components/Logo";

export default function MyPage() {
  return (
    <Logo 
      href="/" 
      size="md" 
      showText={true}
      logoPath="/custom-logo.png"
      alt="Custom Logo"
      text="Custom Brand"
    />
  );
}
```

### Mengubah Konfigurasi Logo

Edit file `lib/logo-config.ts`:

```typescript
export const LOGO_CONFIG: LogoConfig = {
  path: "/bagana-ai-logo.png",
  alt: "BAGANA AI Logo",
  text: "BAGANA AI",
  href: "/",
  size: "md",
  showText: true,
  className: "",
  position: "left", // Posisi: "left" (pojok kiri) | "center" (tengah) | "right" (pojok kanan)
};
```

### Mengubah Posisi Logo

**Posisi di Pojok Kiri (Default):**
```typescript
import { setLogoPosition } from "@/lib/logo-config";

setLogoPosition("left"); // Logo di kiri, menu di kanan
```

**Posisi di Tengah Header:**
```typescript
setLogoPosition("center"); // Logo di tengah, menu di bawahnya
```

**Posisi di Pojok Kanan:**
```typescript
setLogoPosition("right"); // Logo di kanan, menu di kiri
```

### Mengubah Logo Secara Programatik

```typescript
import { setLogoPath, setLogoText, setLogoPosition, updateLogoConfig } from "@/lib/logo-config";

// Ubah path logo
setLogoPath("/new-logo.png");

// Ubah text logo
setLogoText("NEW BRAND");

// Ubah posisi logo (left, center, right)
setLogoPosition("left"); // Pojok kiri (default)
setLogoPosition("center"); // Tengah header
setLogoPosition("right"); // Pojok kanan

// Update multiple properties
updateLogoConfig({
  path: "/custom-logo.png",
  text: "Custom Brand",
  size: "lg",
  showText: true,
  position: "left", // Posisi logo
});
```

### Menggunakan Hook untuk Logo Dinamis

```tsx
"use client";

import { useLogo } from "@/lib/hooks/useLogo";
import { Logo } from "@/components/Logo";

export default function MyPage() {
  const { config, refresh } = useLogo(true); // auto-refresh enabled

  return (
    <Logo 
      dynamic={true}
      // Props akan di-override oleh config jika tidak disediakan
    />
  );
}
```

## Fitur

1. **Logo Dinamis**: Logo dapat dikonfigurasi tanpa mengubah komponen
2. **Posisi Dinamis**: Logo dapat diposisikan di kiri, tengah, atau kanan header
3. **Props Override**: Props manual dapat mengoverride konfigurasi dinamis
4. **Default Values**: Selalu ada fallback ke nilai default
5. **Backward Compatible**: Tetap mendukung penggunaan manual logo props
6. **Easy Configuration**: Semua konfigurasi di satu tempat

## Perluasan di Masa Depan

Hook `useLogo` dapat diperluas untuk:
- Fetch logo config dari API
- Load logo config dari database
- Real-time updates dari websocket
- Multi-tenant logo (berbeda per user/organization)

Contoh implementasi API:

```typescript
// lib/hooks/useLogo.ts
const refresh = async () => {
  const response = await fetch('/api/logo-config');
  const data = await response.json();
  setConfig(data);
};
```

## Contoh Konfigurasi

### Logo dengan Text
```typescript
updateLogoConfig({
  path: "/logo.png",
  text: "BAGANA AI",
  showText: true,
  size: "md",
});
```

### Logo tanpa Text
```typescript
updateLogoConfig({
  path: "/logo-icon.png",
  showText: false,
  size: "sm",
});
```

### Logo Custom dengan Link
```typescript
updateLogoConfig({
  path: "/custom-logo.png",
  text: "Custom Brand",
  href: "/custom-home",
  size: "lg",
  showText: true,
});
```

### Logo di Pojok Kiri (Default)
```typescript
updateLogoConfig({
  position: "left", // Logo di pojok kiri, menu di kanan
});
```

### Logo di Tengah Header
```typescript
updateLogoConfig({
  position: "center", // Logo di tengah, menu di bawahnya
});
```

### Logo di Pojok Kanan
```typescript
updateLogoConfig({
  position: "right", // Logo di pojok kanan, menu di kiri
});
```
