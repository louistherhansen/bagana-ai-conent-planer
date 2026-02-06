# Dynamic Navigation Menu

## Overview

Navigation menu telah diubah menjadi dinamis dan dapat dikonfigurasi dengan mudah melalui file konfigurasi.

## Struktur

### File Konfigurasi
- **`lib/nav-config.ts`**: File konfigurasi utama untuk menu navigasi
  - `NAV_CONFIG`: Array konfigurasi menu items
  - `getNavItems()`: Fungsi untuk mendapatkan menu items yang visible
  - `getNavItem(href)`: Fungsi untuk mendapatkan item berdasarkan href
  - `setNavItemVisible(href, visible)`: Fungsi untuk mengubah visibility item
  - `upsertNavItem(item)`: Fungsi untuk menambah/update item

### Komponen
- **`components/AppNav.tsx`**: Komponen navigasi yang mendukung mode dinamis
  - Props `dynamic`: Aktifkan mode dinamis (default: false)
  - Props `items`: Menu items manual (opsional jika dynamic=true)
  - Mendukung badge pada menu items

- **`components/PageLayout.tsx`**: Layout wrapper dengan menu dinamis
  - Props `dynamicMenu`: Aktifkan menu dinamis (default: true)

- **`components/Logo.tsx`**: Komponen logo yang diperbarui
  - Props `logoPath`: Custom path untuk logo
  - Props `alt`: Custom alt text
  - Hover effects yang lebih baik

### Hook
- **`lib/hooks/useNavItems.ts`**: React hook untuk menu dinamis
  - Dapat diperluas untuk fetch dari API di masa depan
  - Support auto-refresh

## Penggunaan

### Menggunakan Menu Dinamis (Default)

```tsx
import { PageLayout } from "@/components/PageLayout";

export default function MyPage() {
  return (
    <PageLayout currentPath="/dashboard">
      {/* Content */}
    </PageLayout>
  );
}
```

### Menggunakan Menu Manual

```tsx
import { AppNav } from "@/components/AppNav";
import { getNavItems } from "@/lib/nav-config";

export default function MyPage() {
  return (
    <AppNav items={getNavItems()} currentPath="/dashboard" />
  );
}
```

### Mengubah Menu Items

Edit file `lib/nav-config.ts`:

```typescript
export const NAV_CONFIG: NavItem[] = [
  { href: "/", label: "Home", order: 1, visible: true },
  { href: "/chat", label: "Chat", order: 2, visible: true },
  // Tambah/edit item di sini
];
```

### Menyembunyikan Menu Item

```typescript
import { setNavItemVisible } from "@/lib/nav-config";

// Sembunyikan menu item
setNavItemVisible("/settings", false);
```

### Menambah Menu Item Baru

```typescript
import { upsertNavItem } from "@/lib/nav-config";

upsertNavItem({
  href: "/new-page",
  label: "New Page",
  order: 13,
  visible: true,
  badge: "New"
});
```

## Fitur

1. **Menu Dinamis**: Menu dapat dikonfigurasi tanpa mengubah komponen
2. **Ordering**: Menu items dapat diurutkan dengan property `order`
3. **Visibility**: Menu items dapat disembunyikan dengan property `visible`
4. **Badge Support**: Menu items dapat menampilkan badge
5. **Backward Compatible**: Tetap mendukung penggunaan manual menu items

## Perluasan di Masa Depan

Hook `useNavItems` dapat diperluas untuk:
- Fetch menu items dari API
- Load menu items dari database
- Real-time updates dari websocket
- Role-based menu items

Contoh implementasi API:

```typescript
// lib/hooks/useNavItems.ts
const refresh = async () => {
  const response = await fetch('/api/nav-items');
  const data = await response.json();
  setItems(data);
};
```
