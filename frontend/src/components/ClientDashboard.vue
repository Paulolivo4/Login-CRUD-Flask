<template>
  <div class="client-layout">
    <nav class="navbar">
      <div class="nav-content">
        <h1 class="logo">🍽️ Tasty App</h1>
        <div class="user-menu">
          <span class="welcome-text">Hola, <strong>{{ auth.user?.name || 'Usuario' }}</strong></span>
          <button @click="logout" class="btn-logout">Cerrar Sesión</button>
        </div>
      </div>
    </nav>

    <main class="container">
      <div v-if="!selectedRestaurant" class="view-section">
        <h2 class="section-title">Elige un Restaurante</h2>
        <div class="grid">
          <div v-for="rest in restaurants" :key="rest.id" class="restaurant-card" @click="selectRestaurant(rest)">
            <div class="card-image" :style="{ backgroundImage: `url(${rest.foto || 'https://via.placeholder.com/400x250?text=Restaurante'})` }"></div>
            <div class="card-info">
              <h3>{{ rest.nombre }}</h3>
              <p>📍 {{ rest.direccion }}</p>
              <span class="hours-tag">🕒 {{ rest.horario }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="view-section">
        <button class="btn-back" @click="selectedRestaurant = null">← Volver a restaurantes</button>
        <h2 class="section-title">Menú de {{ selectedRestaurant.nombre }}</h2>
        <div class="grid">
          <div v-for="dish in menu" :key="dish.id" class="dish-card">
            <div class="card-image" :style="{ backgroundImage: `url(${dish.foto || 'https://via.placeholder.com/400x250?text=Comida'})` }"></div>
            <div class="card-info">
              <div class="dish-header">
                <h3>{{ dish.nombre }}</h3>
                <span class="price">${{ dish.precio }}</span>
              </div>
              <p class="description">{{ dish.descripcion }}</p>
              <button class="btn-reserve" @click="openCheckout(dish)">Reservar y Pagar</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showCheckout" class="modal-overlay">
      <div class="modal-content payment-premium">
        <header class="modal-header">
          <h3>Finalizar Reserva</h3>
          <button @click="showCheckout = false" class="close-btn">&times;</button>
        </header>

        <div :class="['credit-card-visual', cardBrand.toLowerCase()]">
          <div class="card-glass"></div>
          <div class="card-chip"></div>
          <div class="card-number">{{ payment.cardNumber || '**** **** **** ****' }}</div>
          <div class="card-bottom">
            <div class="card-holder">
              <small>TITULAR</small>
              <div class="name-display">{{ form.client_name || 'NOMBRE COMPLETO' }}</div>
            </div>
            <div class="card-brand-display">
              <span v-if="cardBrand">{{ cardBrand }}</span>
              <span v-else>CARD</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="processPayment" class="checkout-form">
          <div class="input-grid">
            <div class="group full">
              <label>Correo para Comprobante (Real)</label>
              <input v-model="form.email_real" type="email" placeholder="tu-correo-real@gmail.com" required />
            </div>

            <div class="group full">
              <label>Titular de la Tarjeta</label>
              <input v-model="form.client_name" type="text" placeholder="Ej. Sabrina Perez" required />
            </div>

            <div class="group">
              <label>Fecha y Hora de Reserva</label>
              <input v-model="form.date" type="datetime-local" required />
            </div>

            <div class="group">
              <label>Personas</label>
              <input v-model="form.people" type="number" min="1" required />
            </div>

            <div class="group">
              <label>Número de Tarjeta</label>
              <input v-model="payment.cardNumber" @input="handleCardInput" maxlength="19" placeholder="4555..." required />
            </div>

            <div class="group small">
              <label>CVC</label>
              <input v-model="payment.cvv" type="password" maxlength="4" placeholder="***" required />
            </div>
          </div>

          <div class="summary-box">
            <span>Total a transferir: <strong>${{ calculateTotal }}</strong></span>
          </div>

          <button type="submit" class="btn-confirm-pay" :disabled="loading">
            {{ loading ? 'Procesando Pago...' : 'PAGAR AHORA' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const auth = useAuthStore();

// Estados
const restaurants = ref([]);
const selectedRestaurant = ref(null);
const menu = ref([]);
const showCheckout = ref(false);
const selectedDish = ref(null);
const loading = ref(false);

// Formulario
const form = ref({ email_real: '', client_name: '', date: '', people: 1 });
const payment = ref({ cardNumber: '', expiry: '', cvv: '' });
const cardBrand = ref('');

onMounted(async () => {
  // Llama a /client/restaurants (Axios le pega el /api al inicio automáticamente)
  const res = await axios.get('/client/restaurants');
  restaurants.value = res.data;
});

const selectRestaurant = async (rest) => {
  selectedRestaurant.value = rest;
  // Ajusta esta ruta a como la tengas en tu controller de menús
  const res = await axios.get(`/client/restaurant/${rest.id}/menus`);
  menu.value = res.data;
};


const openCheckout = (dish) => {
  selectedDish.value = dish;
  showCheckout.value = true;
};

const handleCardInput = (e) => {
  let value = e.target.value.replace(/\D/g, '');
  payment.value.cardNumber = value.replace(/(\d{4})(?=\d)/g, '$1 ');
  detectCard(value);
};

const detectCard = (num) => {
  if (/^4/.test(num)) cardBrand.value = "Visa";
  else if (/^5[1-5]/.test(num)) cardBrand.value = "Mastercard";
  else if (/^3[47]/.test(num)) cardBrand.value = "Amex";
  else if (/^6(?:011|5)/.test(num)) cardBrand.value = "Discover";
  else if (/^3(?:0[0-5]|[68])/.test(num)) cardBrand.value = "Diners";
  else cardBrand.value = "";
};

const calculateTotal = computed(() => {
  if (!selectedDish.value) return 0;
  return (selectedDish.value.precio * form.value.people).toFixed(2);
});

const processPayment = async () => {
  loading.value = true;
  try {
    await axios.post('/client/reserve', {
      email_real: form.value.email_real,
      client_name: form.value.client_name,
      restaurant_id: selectedRestaurant.value.id,
      menu_id: selectedDish.value.id,
      menu_name: selectedDish.value.nombre,
      date: form.value.date,
      people: form.value.people,
      total: calculateTotal.value,
      card_brand: cardBrand.value || 'Generica'
    });

    alert('¡Éxito! Pago procesado y comprobante enviado a tu correo real.');
    showCheckout.value = false;
    selectedRestaurant.value = null;
  } catch (error) {
    alert('Error: ' + (error.response?.data?.error || 'Falló la conexión'));
  } finally {
    loading.value = false;
  }
};

const logout = () => { auth.logout(); router.push('/login'); };
</script>

<style scoped>
.client-layout { background: #f0f2f5; min-height: 100vh; font-family: 'Inter', sans-serif; }
.navbar { background: #ffffff; padding: 15px 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.nav-content { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; }
.logo { color: #4f46e5; font-weight: 800; }
.btn-logout { background: #fee2e2; color: #dc2626; border: none; padding: 8px 15px; border-radius: 8px; cursor: pointer; }

.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.section-title { margin-bottom: 30px; font-size: 1.8rem; color: #1f2937; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }

/* CARDS */
.restaurant-card, .dish-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: 0.3s; }
.restaurant-card:hover { transform: translateY(-5px); cursor: pointer; }
.card-image { height: 180px; background-size: cover; background-position: center; }
.card-info { padding: 20px; }
.hours-tag { background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

.dish-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.price { color: #10b981; font-weight: 800; font-size: 1.2rem; }
.btn-reserve { width: 100%; background: #4f46e5; color: white; border: none; padding: 12px; border-radius: 10px; font-weight: 700; cursor: pointer; margin-top: 15px; }

/* MODAL PREMIUM */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; z-index: 2000; }
.payment-premium { background: white; padding: 30px; border-radius: 24px; width: 480px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
.modal-header { display: flex; justify-content: space-between; margin-bottom: 20px; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; }

/* TARJETA VISUAL */
.credit-card-visual {
  height: 200px; background: linear-gradient(135deg, #333 0%, #111 100%);
  border-radius: 18px; padding: 25px; color: white; position: relative; margin-bottom: 30px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2); overflow: hidden; transition: 0.5s;
}
.credit-card-visual.visa { background: linear-gradient(135deg, #1a1f71 0%, #0079c1 100%); }
.credit-card-visual.mastercard { background: linear-gradient(135deg, #eb001b 0%, #ff5f00 100%); }
.card-chip { width: 45px; height: 35px; background: #e5c05b; border-radius: 6px; margin-bottom: 30px; }
.card-number { font-size: 1.4rem; letter-spacing: 3px; font-family: 'Courier New', monospace; margin-bottom: 25px; }
.card-bottom { display: flex; justify-content: space-between; align-items: flex-end; }
.name-display { font-weight: bold; text-transform: uppercase; font-size: 0.9rem; }

/* FORM */
.input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.full { grid-column: span 2; }
label { font-size: 0.75rem; font-weight: 700; color: #6b7280; text-transform: uppercase; }
input { width: 100%; padding: 12px; border: 1px solid #e5e7eb; border-radius: 10px; margin-top: 5px; background: #f9fafb; }

.summary-box { background: #f3f4f6; padding: 15px; border-radius: 12px; margin-top: 20px; text-align: center; }
.btn-confirm-pay { width: 100%; background: #10b981; color: white; border: none; padding: 16px; border-radius: 12px; font-weight: 800; font-size: 1rem; cursor: pointer; margin-top: 20px; }
</style>