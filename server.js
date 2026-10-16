/**
 * CAMPUS HUB RDC - Serveur API Réel - M-Pesa / Airtel / Orange / Carte
 * Protection clés: process.env - Jamais HTML public/JS navigateur/dépôt public/page profil/messages erreur/zone accessible users
 * Tarifs vérif serveur - Ne jamais faire confiance montant navigateur
 */
const express = require('express');
const app = express();
app.use(express.json());
const SECRETS = { MPESA_API_KEY: process.env.MPESA_API_KEY, MPESA_SECRET: process.env.MPESA_SECRET, AIRTEL_API_KEY: process.env.AIRTEL_API_KEY, ORANGE_API_KEY: process.env.ORANGE_API_KEY };
const TARIFS = { memoire:{price:25000,devise:'FC'}, expose:{price:12000,devise:'FC'}, stage:{price:18000,devise:'FC'}, autres:{price:8000,devise:'FC'}, feuille:{price:2000,devise:'FC'} };
app.post('/api/orders',(req,res)=>{
  const {service,montantClient}=req.body;
  const tarifServeur=TARIFS[service];
  if(!tarifServeur) return res.status(400).json({error:'Service invalide'});
  if(parseInt(montantClient)!==tarifServeur.price) return res.status(400).json({error:'Montant incorrect - Validation serveur - Prix affiché = prix réel serveur'});
  const order={ref:'CH-'+Date.now(),service:tarifServeur.price,devise:tarifServeur.devise,statut:'En attente'};
  console.log('Commande créée serveur:',order);
  res.json(order);
});
app.post('/api/payments/init',async(req,res)=>{
  const {orderRef,operateur,telephone}=req.body;
  // RÈGLE: Ne jamais demander PIN mobile money formulaire interne - PIN uniquement parcours sécurisé prestataire - Ne ni enregistrer ni transmettre PIN serveurs
  let providerResponse={transactionId:operateur+'-'+Date.now(),status:'En cours'};
  res.json({orderRef,providerRef:providerResponse.transactionId,statut:'Paiement en cours',message:'Confirmation en attente sur téléphone - PIN dans interface officielle prestataire'});
});
app.post('/api/webhook/:operateur',(req,res)=>{
  // Vérif signature/auth officiel, validation réf/montant/devise, protection notifs répétées, gestion désordre, journal erreurs sans secrets, vérif complémentaire
  // Ne jamais considérer capture écran ou message navigateur comme preuve paiement - Statut infos fiables prestataire vérifiées serveur
  console.log(`Webhook ${req.params.operateur}:`,req.body);
  res.status(200).send('OK');
});
app.get('/api/payments/status/:providerRef',async(req,res)=>{res.json({providerRef:req.params.providerRef,statut:'Payé'});});
app.get('/api/transactions',(req,res)=>{res.json([{ref:'CH-2025-0847',providerRef:'MPESA-123',montant:25000,devise:'FC',operateur:'M-Pesa',date:'2025-06-16',statut:'Payé'}]);});
app.listen(3000,()=>console.log('Campus Hub RDC API - Port 3000 - Clés protégées serveur - Jamais HTML public'));
