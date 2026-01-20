import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// IMPORTACIÓN DE COMPONENTES
import Login from '../components/Login.vue';
import AdminDashboard from '../components/AdminDashboard.vue';
import AdminCreateRestaurant from '../components/AdminCreateRestaurant.vue';
import OwnerDashboard from '../components/OwnerDashboard.vue';
import ClientDashboard from '../components/ClientDashboard.vue';
import Register from '../components/Register.vue'; // <-- Asegúrate de tener este archivo
import ForgotPassword from '../components/ForgotPassword.vue'; // <-- Asegúrate de tener este archivo

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: Login },
    
    // RUTAS PÚBLICAS (Nuevas)
    { path: '/register', name: 'Register', component: Register },
    { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
    { 
      path: '/reset-password', 
      name: 'ResetPassword', 
      component: () => import('../components/ResetPassword.vue') 
    },

    // ROL 1: ADMINISTRADOR
    { 
      path: '/admin/dashboard', 
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 1 } 
    },
    { 
      path: '/admin/restaurants/create', 
      name: 'CreateRestaurant',
      component: AdminCreateRestaurant, 
      meta: { requiresAuth: true, role: 1 } 
    },

    // ROL 2: DUEÑO
    { 
      path: '/owner/dashboard', 
      name: 'OwnerDashboard',
      component: OwnerDashboard, 
      meta: { requiresAuth: true, role: 2 } 
    },

    // ROL 3: CLIENTE
    { 
      path: '/client/dashboard', 
      name: 'ClientDashboard',
      component: ClientDashboard, 
      meta: { requiresAuth: true, role: 3 } 
    },

    // Redirección por defecto
    { path: '/:pathMatch(.*)*', redirect: '/login' }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// GUARDIA DE NAVEGACIÓN
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    
    // 1. Si la ruta NO requiere auth (Login, Register, Forgot), dejar pasar
    if (!to.meta.requiresAuth) {
        next();
        return;
    }

    // 2. Si requiere auth, verificar sesión
    if (!authStore.isAuthenticated) {
        await authStore.checkSession();
    }

    if (!authStore.isAuthenticated) {
        next('/login');
        return;
    }

    // 3. Verificar Rol
    const userRole = parseInt(authStore.user?.role); 
    const requiredRole = to.meta.role;

    if (requiredRole && userRole !== requiredRole) {
        if (userRole === 1) next('/admin/dashboard');
        else if (userRole === 2) next('/owner/dashboard');
        else if (userRole === 3) next('/client/dashboard');
        else next('/login');
        return;
    }

    next();
});

export default router;