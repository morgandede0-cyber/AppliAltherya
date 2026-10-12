export const bankMarkup = `<div id="bank-polished">

<img class="heading" src="/assets/bank-ui/heading.webp" alt="Banque de IV — Altherya">
<section class="ledger" aria-label="Vos soldes">
<div class="account" style="--panel:url(/assets/bank-ui/wallet.webp)"><output data-wallet aria-label="Portefeuille">1 250 Gold</output></div>
<div class="account" style="--panel:url(/assets/bank-ui/bank.webp)"><output data-bank aria-label="Banque">850 Gold</output></div>
<div class="account" style="--panel:url(/assets/bank-ui/fortune.webp)"><output data-fortune aria-label="Fortune">2 100 Gold</output></div>
</section>
<section class="operations" aria-label="Opérations bancaires">
<form class="transaction" data-mode="deposit" style="--panel:url(/assets/bank-ui/deposit.webp)" aria-label="Déposer">
<div class="amount-row"><button type="button" class="cursor-interaction" data-step="-100" aria-label="Diminuer le dépôt"><img src="/assets/bank-ui/minus.webp" alt=""></button><input aria-label="Montant à déposer" type="number" min="1" step="1" value="100"><button type="button" class="cursor-interaction" data-step="100" aria-label="Augmenter le dépôt"><img src="/assets/bank-ui/plus.webp" alt=""></button></div>
<div class="presets"><button type="button" class="cursor-interaction" data-preset="100" aria-label="Déposer 100 Gold"><img src="/assets/bank-ui/100.webp" alt="100"></button><button type="button" class="cursor-interaction" data-preset="500" aria-label="Déposer 500 Gold"><img src="/assets/bank-ui/500.webp" alt="500"></button><button type="button" class="cursor-interaction" data-preset="all" aria-label="Déposer tout"><img src="/assets/bank-ui/all.webp" alt="Tout"></button></div>
<p class="fee-note" aria-hidden="true"></p><button type="submit" class="confirm cursor-interaction" aria-label="Confirmer le dépôt"><img src="/assets/bank-ui/deposit-confirm.webp" alt="Confirmer le dépôt"></button>
</form>

<form class="transaction" data-mode="withdraw" style="--panel:url(/assets/bank-ui/withdraw.webp)" aria-label="Retirer">
<div class="amount-row"><button type="button" class="cursor-interaction" data-step="-100" aria-label="Diminuer le retrait"><img src="/assets/bank-ui/minus.webp" alt=""></button><input aria-label="Montant à retirer" type="number" min="1" step="1" value="100"><button type="button" class="cursor-interaction" data-step="100" aria-label="Augmenter le retrait"><img src="/assets/bank-ui/plus.webp" alt=""></button></div>
<div class="presets"><button type="button" class="cursor-interaction" data-preset="100" aria-label="Retirer 100 Gold"><img src="/assets/bank-ui/100.webp" alt="100"></button><button type="button" class="cursor-interaction" data-preset="500" aria-label="Retirer 500 Gold"><img src="/assets/bank-ui/500.webp" alt="500"></button><button type="button" class="cursor-interaction" data-preset="all" aria-label="Retirer tout"><img src="/assets/bank-ui/all.webp" alt="Tout"></button></div>
<p class="fee-note" data-withdraw-quote></p><button type="submit" class="confirm cursor-interaction" aria-label="Confirmer le retrait"><img src="/assets/bank-ui/withdraw-confirm.webp" alt="Confirmer le retrait"></button>
</form>
</section>
<button class="back cursor-interaction" type="button" aria-label="Retour en ville"><img src="/assets/bank-ui/back.webp" alt="Retour en ville"></button>
<p class="status" role="status" aria-live="polite"></p>

</div>
`;
