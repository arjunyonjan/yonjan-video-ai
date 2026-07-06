function speedBar(honorSec) {
  const rtx3060 = (honorSec * 0.07).toFixed(1);
  const rtx5060 = (honorSec * 0.035).toFixed(1);
  return `
    <div class="mt-4 pt-4 border-t border-white/5 space-y-2">
      <div class="text-xs text-gray-600 font-medium uppercase tracking-wider mb-2">Speed Comparison</div>
      <div class="flex items-center gap-2 text-xs">
        <span class="w-20 text-gray-500">Honor 90</span>
        <div class="flex-1 h-3 rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-amber-500/70" style="width: 100%"></div>
        </div>
        <span class="w-14 text-right text-amber-400">~${honorSec}s</span>
      </div>
      <div class="flex items-center gap-2 text-xs">
        <span class="w-20 text-gray-500">RTX 3060</span>
        <div class="flex-1 h-3 rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-emerald-500/70" style="width: 7%"></div>
        </div>
        <span class="w-14 text-right text-emerald-400">~${rtx3060}s</span>
      </div>
      <div class="flex items-center gap-2 text-xs">
        <span class="w-20 text-gray-500">RTX 5060</span>
        <div class="flex-1 h-3 rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-sky-500/70" style="width: 3.5%"></div>
        </div>
        <span class="w-14 text-right text-sky-400">~${rtx5060}s</span>
      </div>
    </div>`;
}
