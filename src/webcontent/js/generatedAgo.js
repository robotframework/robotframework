function get_end(number) {
  if (number == 1) { return ' '; }
  return 's ';
}
function get_sec_str(secs) {
  return secs + ' second' + get_end(secs);
}
function get_min_str(mins) {
  return mins + ' minute' + get_end(mins);
}
function get_hour_str(hours) {
  return hours + ' hour' + get_end(hours);
}
function get_day_str(days) {
  return days + ' day' + get_end(days);
}
function get_year_str(years) {
  return years + ' year' + get_end(years);
}
var generated = Math.round(window.testdata.generated().getTime() / 1000);
current = Math.round(new Date().getTime() / 1000);
elapsed = current - generated;

if (elapsed < 0) {
  elapsed = Math.abs(elapsed);
  prefix = '- ';
}
else {
  prefix = '';
}
secs  = elapsed % 60;
mins  = Math.floor(elapsed / 60) % 60;
hours = Math.floor(elapsed / (60*60)) % 24;
days  = Math.floor(elapsed / (60*60*24)) % 365;
years = Math.floor(elapsed / (60*60*24*365));
if (years > 0) {
  // compensate the effect of leap years (not perfect but should be enough)
  days = days - Math.floor(years / 4);
  if (days < 0) { days = 0; }
  output = get_year_str(years) + get_day_str(days);
}
else if (days > 0) {
  output = get_day_str(days) +  get_hour_str(hours);
}
else if (hours > 0) {
  output = get_hour_str(hours) + get_min_str(mins);
}
else if (mins > 0) {
  output = get_min_str(mins) + get_sec_str(secs);
}
else {
  output = get_sec_str(secs);
}