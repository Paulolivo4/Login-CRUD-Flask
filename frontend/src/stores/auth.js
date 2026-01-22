import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        isAuthenticated: false
    }),
    actions: {
        async login(email, password) {
            try {
                // Flask usa cookies, axios las maneja con withCredentials: true
                const response = await axios.post('/login', { email, password });
                
                this.user = response.data.user;
                this.isAuthenticated = true;

                // Redirección basada en el rol
                this.redirectByRole(this.user.role);
                
                // IMPORTANTE: Retornamos la data para que el componente Login pueda usarla si la necesita
                return response.data;
                
            } catch (error) {
                this.user = null;
                this.isAuthenticated = false;
                throw error; 
            }
        },

        async checkSession() {
            try {
                const response = await axios.get('/check_session');
                this.user = response.data.user;
                this.isAuthenticated = true;
            } catch (error) {
                this.user = null;
                this.isAuthenticated = false;
                // Si la sesión expira y no estamos en login, redirigir
                if (router.currentRoute.value.path !== '/login') {
                    router.push('/login');
                }
            }
        },

        async logout() {
            try {
                await axios.post('/logout');
            } catch (e) {
                console.error("Error en logout", e);
            } finally {
                this.user = null;
                this.isAuthenticated = false;
                router.push('/login');
            }
        },

        redirectByRole(role) {
            // Convertimos a número por seguridad
            const roleId = parseInt(role);
            
            console.log("Redirigiendo usuario con rol:", roleId);

            if (roleId === 1) {
                router.push('/admin/dashboard');
            } else if (roleId === 2) {
                router.push('/owner/dashboard');
            } else if (roleId === 3) {
                // CORRECCIÓN: Apuntamos a la nueva ruta que creamos en el router
                router.push('/client/dashboard'); 
            } else {
                router.push('/login');
            }
        }
    }
});