import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';

const rust = Color(0xFFC1440E), charcoal = Color(0xFF1E1B1A), sand = Color(0xFFE8D5B5), muted = Color(0xFF8E3B34);
const _tb = 'https://trek.nasa.gov/tiles/Mars/EQ/';
const _tt = '1.0.0/default/default028mm/{z}/{y}/{x}.jpg';
const imgUrl = '${_tb}Mars_Viking_MDIM21_ClrMosaic_global_232m/$_tt';
const demUrl = '${_tb}Mars_MGS_MOLA_ClrShade_merge_global_463m/$_tt';
const attribution = 'Imagery & elevation: NASA Mars Trek (Viking MDIM2.1, MGS MOLA). Maps: USGS Astrogeology. '
    'Rover references: NASA/JPL-Caltech. MARSCOPE is independent and not affiliated with or endorsed by NASA.';
double d(x) => (x as num).toDouble();
LatLng ll(m) => LatLng(d(m['lat']), d(m['lon']));
String fc(LatLng p) => '${p.latitude.toStringAsFixed(3)}°, ${p.longitude.toStringAsFixed(3)}°';
Future<void> open(String u) => launchUrl(Uri.parse(u), mode: LaunchMode.externalApplication);

class S extends ChangeNotifier {
  String base = const String.fromEnvironment('API', defaultValue: 'http://10.0.2.2:5000'); // emulator -> host
  bool img = true, dem = false, haz = true, poi = true, busy = false;
  LatLng? sel, start, end;
  Map? loc;
  List hazards = [], pois = [], routes = [];
  int ri = 0;
  String? err;
  void up() => notifyListeners();
  Future get(String p) async => jsonDecode((await http.get(Uri.parse('$base$p')).timeout(const Duration(seconds: 30))).body);
  Future load() async {
    try { hazards = await get('/api/hazards'); pois = await get('/api/pois'); err = null; }
    catch (e) { err = 'Backend unreachable at $base'; }
    up();
  }
  Future pick(LatLng p) async {
    sel = p; loc = null; up();
    try { loc = await get('/api/location?lat=${p.latitude}&lon=${p.longitude}'); } catch (e) { err = '$e'; }
    up();
  }
  Future plan() async {
    if (start == null || end == null) return;
    busy = true; err = null; up();
    try {
      routes = await get('/api/route?slat=${start!.latitude}&slon=${start!.longitude}&elat=${end!.latitude}&elon=${end!.longitude}');
      ri = 0;
    } catch (e) { err = 'Route failed: $e'; }
    busy = false; up();
  }
  String summary() {
    if (routes.isEmpty) return 'No route planned yet. Pick a start and destination on the map, then plan a route.';
    final r = routes[ri];
    final b = StringBuffer('MARSCOPE EXPLORATION SUMMARY\n\nRoute: ${r['name']}\n')
      ..writeln('Start: ${fc(start!)}  (~${r['elev_start_m']} m)')
      ..writeln('End:   ${fc(end!)}  (~${r['elev_end_m']} m)')
      ..writeln('Distance: ${r['distance_km']} km (approx.)')
      ..writeln('Max estimated slope: ${r['max_slope_deg']}°  (coarse model)')
      ..writeln('Waypoints: ${(r['points'] as List).length}\n\nHazards along route:');
    final hs = r['hazards'] as List;
    if (hs.isEmpty) b.writeln('  none mapped');
    for (final h in hs) { b.writeln('  - ${h['name']} (${h['type']}, severity ${h['severity']}/3)'); }
    b.writeln('\nScientific points of interest nearby:');
    final ps = r['pois'] as List;
    if (ps.isEmpty) b.writeln('  none within 150 km');
    for (final p in ps) { b.writeln('  - $p'); }
    return '$b\nData note: elevations/hazards are approximate, curated from NASA/USGS references; not for real navigation.\n$attribution';
  }
}
final s = S();
final mc = MapController();

void main() => runApp(MaterialApp(
      title: 'MARSCOPE', debugShowCheckedModeBanner: false,
      theme: ThemeData(brightness: Brightness.dark, useMaterial3: true, scaffoldBackgroundColor: charcoal,
          colorScheme: const ColorScheme.dark(primary: rust, secondary: sand, surface: Color(0xFF2A2523)),
          appBarTheme: const AppBarTheme(backgroundColor: charcoal)),
      home: const Welcome()));

class Logo extends StatelessWidget {
  final double size; const Logo(this.size, {super.key});
  @override Widget build(BuildContext c) => CustomPaint(size: Size(size, size), painter: _LP());
}
class _LP extends CustomPainter {
  @override void paint(Canvas c, Size z) {
    final m = z.center(Offset.zero);
    for (var i = 4; i >= 1; i--) {
      c.drawCircle(m + Offset(i * 1.5, -i * 1.0), z.width / 2 * i / 4.4,
          Paint()..style = PaintingStyle.stroke..strokeWidth = 2..color = i == 1 ? sand : rust.withOpacity(.4 + .15 * i));
    }
    c.drawCircle(m, z.width * .09, Paint()..color = rust);
    final p = Paint()..color = sand..strokeWidth = 2;
    c.drawLine(m + Offset(0, -z.width * .22), m + Offset(0, z.width * .22), p);
    c.drawLine(m + Offset(-z.width * .22, 0), m + Offset(z.width * .22, 0), p);
  }
  @override bool shouldRepaint(_) => false;
}

class Welcome extends StatelessWidget {
  const Welcome({super.key});
  @override Widget build(BuildContext c) => Scaffold(
      body: Center(child: Padding(padding: const EdgeInsets.all(28), child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Logo(150), const SizedBox(height: 20),
        const Text('MARSCOPE', style: TextStyle(fontSize: 34, letterSpacing: 6, color: sand, fontWeight: FontWeight.bold)),
        const Text('Martian Exploration & Survival Companion', style: TextStyle(color: rust)),
        const SizedBox(height: 14),
        const Text('Explore the Red Planet. Navigate Beyond Boundaries.', textAlign: TextAlign.center),
        const SizedBox(height: 30),
        FilledButton(onPressed: () => Navigator.push(c, MaterialPageRoute(builder: (_) => const Home())), child: const Text('ENTER MISSION DASHBOARD')),
        const SizedBox(height: 24),
        const Text(attribution, textAlign: TextAlign.center, style: TextStyle(fontSize: 10, color: Colors.white54)),
      ]))));
}

class Home extends StatefulWidget { const Home({super.key}); @override State<Home> createState() => _H(); }
class _H extends State<Home> {
  int i = 0;
  @override void initState() { super.initState(); s.load(); }
  void go(int n) => setState(() => i = n);
  @override Widget build(BuildContext c) => Scaffold(
      appBar: AppBar(title: const Text('MARSCOPE'), actions: [
        IconButton(icon: const Icon(Icons.info_outline), onPressed: () => showAboutDialog(context: c, applicationName: 'MARSCOPE', applicationLegalese: attribution))]),
      body: ListenableBuilder(listenable: s, builder: (c, _) => Column(children: [
        if (s.err != null) MaterialBanner(content: Text(s.err!), actions: [TextButton(onPressed: s.load, child: const Text('RETRY'))]),
        Expanded(child: IndexedStack(index: i, children: [MapTab(go), const RouteTab(), HazTab(go), PoiTab(go), const SumTab()])),
      ])),
      bottomNavigationBar: NavigationBar(selectedIndex: i, onDestinationSelected: go, destinations: const [
        NavigationDestination(icon: Icon(Icons.public), label: 'Map'),
        NavigationDestination(icon: Icon(Icons.route), label: 'Route'),
        NavigationDestination(icon: Icon(Icons.warning_amber), label: 'Hazards'),
        NavigationDestination(icon: Icon(Icons.science), label: 'POIs'),
        NavigationDestination(icon: Icon(Icons.description), label: 'Summary')]));
}

void goTo(LatLng p, void Function(int) go) { go(0); mc.move(p, 4); s.pick(p); }

class MapTab extends StatelessWidget {
  final void Function(int) go; const MapTab(this.go, {super.key});
  Marker pin(LatLng p, IconData i, Color col, [VoidCallback? t]) => Marker(point: p, width: 34, height: 34,
      child: GestureDetector(onTap: t, child: Icon(i, color: col, size: 28)));
  @override Widget build(BuildContext c) {
    final r = s.routes.isEmpty ? null : s.routes[s.ri];
    return Stack(children: [
      FlutterMap(mapController: mc, options: MapOptions(crs: const Epsg4326(), initialCenter: const LatLng(10, 60), initialZoom: 2, minZoom: 0, maxZoom: 8, onTap: (_, p) => s.pick(p)), children: [
        if (s.img) TileLayer(urlTemplate: imgUrl, maxNativeZoom: 7, userAgentPackageName: 'app.marscope'),
        if (s.dem) Opacity(opacity: s.img ? .6 : 1, child: TileLayer(urlTemplate: demUrl, maxNativeZoom: 6, userAgentPackageName: 'app.marscope')),
        if (s.haz) CircleLayer(circles: [for (final h in s.hazards) CircleMarker(point: ll(h), radius: d(h['radius_km']) * 1000 * 1.88, useRadiusInMeter: true,
            color: (d(h['severity']) > 2 ? Colors.red : Colors.orange).withOpacity(.25), borderColor: Colors.redAccent, borderStrokeWidth: 1.5)]),
        if (r != null) PolylineLayer(polylines: [Polyline(points: [for (final p in r['points']) LatLng(d(p[0]), d(p[1]))], color: Colors.cyanAccent, strokeWidth: 4)]),
        MarkerLayer(markers: [
          if (s.poi) for (final p in s.pois) pin(ll(p), Icons.star, sand, () => s.pick(ll(p))),
          if (s.start != null) pin(s.start!, Icons.trip_origin, Colors.greenAccent),
          if (s.end != null) pin(s.end!, Icons.flag, Colors.redAccent),
          if (s.sel != null) pin(s.sel!, Icons.place, rust)]),
      ]),
      Positioned(top: 6, left: 6, right: 6, child: Wrap(spacing: 6, children: [
        for (final e in [('Imagery', s.img, () => s.img = !s.img), ('Elevation', s.dem, () => s.dem = !s.dem), ('Hazards', s.haz, () => s.haz = !s.haz), ('POIs', s.poi, () => s.poi = !s.poi)])
          FilterChip(label: Text(e.$1), selected: e.$2, onSelected: (_) { e.$3(); s.up(); })])),
      if (s.sel != null) Positioned(bottom: 8, left: 8, right: 8, child: Card(child: Padding(padding: const EdgeInsets.all(10), child: Column(mainAxisSize: MainAxisSize.min, children: [
        Text(fc(s.sel!), style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(s.loc == null ? 'Loading…' : '~${s.loc!['elevation_m']} m • ${s.loc!['terrain']}', style: const TextStyle(fontSize: 12)),
        Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
          TextButton(onPressed: s.loc == null ? null : () => details(c), child: const Text('Details')),
          TextButton(onPressed: () { s.start = s.sel; s.up(); }, child: const Text('Set start')),
          TextButton(onPressed: () { s.end = s.sel; s.up(); }, child: const Text('Set end'))])])))),
    ]);
  }
  void details(BuildContext c) {
    final l = s.loc!;
    showModalBottomSheet(context: c, isScrollControlled: true, builder: (_) => ListView(padding: const EdgeInsets.all(16), children: [
      Text('Location Details', style: Theme.of(c).textTheme.titleLarge),
      Text('Coordinates: ${fc(s.sel!)}'),
      Text('Elevation (approx.): ${l['elevation_m']} m'),
      Text('Terrain: ${l['terrain']}'),
      Text('Nearest feature: ${l['nearest_feature']} (${l['nearest_km']} km)'),
      Text('Hazards here: ${(l['hazards'] as List).isEmpty ? 'none mapped' : (l['hazards'] as List).map((h) => h['name']).join(', ')}'),
      Text('Environment: ${l['environment']}'),
      const SizedBox(height: 8), const Text('Data sources'),
      for (final u in l['sources']) TextButton(onPressed: () => open(u), child: Text(u, style: const TextStyle(fontSize: 12)))]));
  }
}

class RouteTab extends StatelessWidget {
  const RouteTab({super.key});
  @override Widget build(BuildContext c) => ListView(padding: const EdgeInsets.all(14), children: [
        ListTile(leading: const Icon(Icons.trip_origin, color: Colors.greenAccent), title: Text(s.start == null ? 'Start: select on map → "Set start"' : 'Start: ${fc(s.start!)}')),
        ListTile(leading: const Icon(Icons.flag, color: Colors.redAccent), title: Text(s.end == null ? 'End: select on map → "Set end"' : 'End: ${fc(s.end!)}')),
        FilledButton(onPressed: s.busy ? null : s.plan, child: Text(s.busy ? 'Planning…' : 'PLAN MARSWALK ROUTE')),
        for (var i = 0; i < s.routes.length; i++) Card(color: i == s.ri ? muted.withOpacity(.5) : null, child: ListTile(
            onTap: () { s.ri = i; s.up(); },
            title: Text(s.routes[i]['name']),
            subtitle: Text('${s.routes[i]['distance_km']} km • max slope ${s.routes[i]['max_slope_deg']}° • ${(s.routes[i]['hazards'] as List).length} hazard zone(s)'),
            trailing: i == s.ri ? const Icon(Icons.check_circle, color: sand) : null)),
        const Padding(padding: EdgeInsets.only(top: 12), child: Text('Routes are drawn on the Map tab. Slopes use a coarse elevation model — not for real navigation.', style: TextStyle(fontSize: 11, color: Colors.white54))),
      ]);
}

class HazTab extends StatelessWidget {
  final void Function(int) go; const HazTab(this.go, {super.key});
  @override Widget build(BuildContext c) => ListView(children: [
        for (final h in s.hazards) ListTile(
            leading: Icon(Icons.warning, color: d(h['severity']) > 2 ? Colors.redAccent : Colors.orangeAccent),
            title: Text(h['name']), subtitle: Text('${h['type']} • radius ${h['radius_km']} km • severity ${h['severity']}/3'),
            onTap: () => goTo(ll(h), go))]);
}

class PoiTab extends StatelessWidget {
  final void Function(int) go; const PoiTab(this.go, {super.key});
  @override Widget build(BuildContext c) => ListView(children: [
        for (final p in s.pois) ListTile(
            leading: const Icon(Icons.star, color: sand), title: Text(p['name']), subtitle: Text('${p['type']} — ${p['desc']}'),
            trailing: IconButton(icon: const Icon(Icons.open_in_new), onPressed: () => open(p['src'])),
            onTap: () => goTo(ll(p), go))]);
}

class SumTab extends StatelessWidget {
  const SumTab({super.key});
  @override Widget build(BuildContext c) => ListView(padding: const EdgeInsets.all(14), children: [
        SelectableText(s.summary(), style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
        TextButton.icon(icon: const Icon(Icons.copy), label: const Text('Copy report'), onPressed: () => Clipboard.setData(ClipboardData(text: s.summary()))),
      ]);
}
