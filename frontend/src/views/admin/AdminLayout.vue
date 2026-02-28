<template>
  <div class="admin-layout">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="logo-text">Admin<span>Panel</span></h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin" class="nav-item" exact-active-class="active">Dashboard</router-link>
        <router-link to="/admin/users" class="nav-item" active-class="active">Users</router-link>
        <router-link to="/admin/trips" class="nav-item" active-class="active">Trips & Logs</router-link>
        <router-link to="/admin/cache" class="nav-item" active-class="active">Vector Cache</router-link>
        <div class="divider"></div>
        <router-link to="/" class="nav-item back-home">← Back to App</router-link>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg-light);
  font-family: 'Space Grotesk', sans-serif;
  color: var(--color-text-main);
}

.sidebar {
  width: 250px;
  background-color: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}

.logo-text span {
  color: var(--color-primary);
  margin-left: 0.3rem;
}

.sidebar-nav {
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: block;
  padding: 0.8rem 1rem;
  text-decoration: none;
  color: var(--color-text-muted);
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: var(--color-border);
  color: var(--color-text-main);
}

.nav-item.active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.divider {
  height: 1px;
  background-color: var(--color-border);
  margin: 1rem 0;
}

.back-home {
  color: var(--color-text-main);
  opacity: 0.7;
}

.back-home:hover {
  opacity: 1;
}

.main-content {
  flex: 1;
  padding: 2rem 3rem;
  overflow-y: auto;
}
</style>
