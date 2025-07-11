# Dulcis Fabula - E-commerce per Dolci Artigianali

Un e-commerce completo sviluppato con Django per la vendita di dolci artigianali.

## Funzionalità

- **Catalogo Prodotti**: Navigazione per categorie con ricerca avanzata
- **Carrello**: Gestione carrello con quantità personalizzabili
- **Ordini**: Sistema completo di gestione ordini
- **Recensioni**: Sistema di recensioni e valutazioni
- **Utenti**: Due tipologie di utenti (Clienti e Store Manager)
- **Admin**: Pannello amministrativo personalizzato

## Demo Live

**URL Deployment**: https://dulcis-fabula.up.railway.app/

### Credenziali di Test:
- **Admin**: `admin` / `dfgh781!`
- **Store Manager**: `manager1` / `manager123`  
- **Cliente**: `cliente1` / `password123`

## Tecnologie Utilizzate

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (sviluppo) / PostgreSQL (produzione)
- **Deployment**: Vercel (Django), Cloudinary (asset media)
- **Styling**: Bootstrap 5 + CSS personalizzato

##  Requisiti Tecnici Implementati

###  Struttura Completa (Model, View, Template)
- **3 App Django**: `accounts`, `shop`, `orders`
- **Relazioni tra Modelli**: 
  - Product ↔ Category (ForeignKey)
  - Order ↔ OrderItem (ForeignKey)
  - User ↔ Review (ForeignKey)
- **View Class-based**: `ProductListView` con generics
- **User Personalizzato**: Estensione con campi aggiuntivi
- **2 Gruppi Utenti**: Store Managers e Customers con permessi differenziati

### Sistema Permessi
- **Store Managers**: Gestione prodotti, categorie, ordini
- **Customers**: Creazione recensioni, gestione carrello

## Struttura Database

### Modelli Principali:
- **CustomUser**: Utente esteso con telefono, indirizzo, ruolo
- **Category**: Categorie prodotti con slug e descrizione
- **Product**: Prodotti con specifiche per dolci (ingredienti, allergeni, peso)
- **Review**: Recensioni con rating stellare
- **Cart/CartItem**: Carrello persistente
- **Order/OrderItem**: Sistema ordini completo

## Installazione Locale

1. **Clona il repository**
git clone https://github.com/robertadonato/PPM_ecommerce_project.git
cd dulcis_fabula

2. **Configura ambiente virtuale**
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. **Installa dipendenze**
pip install -r requirements.txt

4. **Configura database**
python manage.py migrate
python manage.py createsuperuser

5. **Carica dati demo**
python manage.py loaddata fixtures.json
python manage.py loaddata users_fixture.json

6. **Avvia server**
python manage.py runserver
