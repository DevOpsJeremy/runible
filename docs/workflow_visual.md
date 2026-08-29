<style>
.graph {
  p {
    display: inline;
  }
}
.success {
  color: green;
  content: ●;
}
.pending {
  color: gray;
}
.running {
  color: yellow;
}
</style>
<div class="graph">
<pre>
   ╭─<p class="running">●</p>
<p class="success">●</p>──┤
   ╰─<p class="running">●</p>──<p class="pending">●</p>
</pre>
</div>
