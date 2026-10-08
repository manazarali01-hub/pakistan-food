/* Pakistan Food original vector icons (2026-10-08).
   Presentation only: no input, navigation or preference mutations. */
(()=>{
  'use strict';
  const base='assets/food-premium-icons.svg#';
  const ns='http://www.w3.org/2000/svg';
  const keys=['rice','chicken','beef','bbq','snacks','breakfast','desserts','drinks','vegetarian','search','phone','mail','pin','home','guide'];
  const pictogram=(name)=>{
    if(!keys.includes(name))return null;
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox','0 0 64 64');
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('focusable','false');
    svg.classList.add('pf-picto');
    const use=document.createElementNS(ns,'use');
    use.setAttribute('href',base+name);
    svg.appendChild(use);
    return svg;
  };
  function enhance(){
    document.querySelectorAll('.category-box[data-category]').forEach(button=>{
      const name=(button.getAttribute('data-category')||'').toLowerCase();
      const slot=button.querySelector(':scope > div:first-child');
      const icon=pictogram(name);
      if(slot&&icon&&!slot.classList.contains('pf-category-icon')){
        slot.replaceChildren(icon);
        slot.classList.add('pf-category-icon');
      }
    });
    const searchSlot=document.querySelector('.search-box > span');
    const searchIcon=pictogram('search');
    if(searchSlot&&searchIcon&&!searchSlot.classList.contains('pf-search-icon')){
      searchSlot.replaceChildren(searchIcon);
      searchSlot.classList.add('pf-search-icon');
    }
    document.querySelectorAll('.contact-card .contact-icon').forEach((slot,i)=>{
      const icon=pictogram(['phone','mail','pin'][i]);
      if(icon&&!slot.classList.contains('pf-contact-icon')){
        slot.replaceChildren(icon);
        slot.classList.add('pf-contact-icon');
      }
    });
    document.querySelectorAll('.dropdown-menu a[data-category-link]').forEach(a=>{
      const name=(a.getAttribute('data-category-link')||'').toLowerCase();
      const icon=pictogram(name);
      if(!icon||a.querySelector('.pf-picto'))return;
      const emoji=['🍚','🍗','🥩','🔥','🥟','🍳','🍮','🥤','🥬'].find(e=>a.textContent.trim().startsWith(e));
      if(emoji)a.textContent=a.textContent.trim().slice(emoji.length).trimStart();
      a.prepend(icon);
      a.classList.add('pf-icon-link');
    });
    const categories=['rice','chicken','beef','bbq','snacks','breakfast','desserts','drinks','vegetarian'];
    document.querySelectorAll('.mobile-menu a[href]').forEach(a=>{
      const found=/^recipes\/([a-z]+)\/$/.exec(a.getAttribute('href')||'');
      if(!found||!categories.includes(found[1])||a.querySelector('.pf-picto'))return;
      a.prepend(pictogram(found[1]));
      a.classList.add('pf-icon-link');
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',enhance,{once:true});
  else enhance();
})();