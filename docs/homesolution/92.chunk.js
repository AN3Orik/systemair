"use strict";
(self.webpackChunk_systemair_portal = self.webpackChunk_systemair_portal || []).push([[92], {
    91092: (t, e, n) => {
        n.d(e, {
            h: () => En
        });
        var r = n(77940);
        function a(t) {
            if (null === t || !0 === t || !1 === t)
                return NaN;
            var e = Number(t);
            return isNaN(e) ? e : e < 0 ? Math.ceil(e) : Math.floor(e)
        }
        function i(t) {
            return i = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(t) {
                return typeof t
            }
            : function(t) {
                return t && "function" == typeof Symbol && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t
            }
            ,
            i(t)
        }
        function o(t, e) {
            if (e.length < t)
                throw new TypeError(t + " argument" + (t > 1 ? "s" : "") + " required, but only " + e.length + " present")
        }
        function u(t) {
            o(1, arguments);
            var e = Object.prototype.toString.call(t);
            return t instanceof Date || "object" === i(t) && "[object Date]" === e ? new Date(t.getTime()) : "number" === typeof t || "[object Number]" === e ? new Date(t) : ("string" !== typeof t && "[object String]" !== e || "undefined" === typeof console || (console.warn("Starting with v2.0.0-beta.1 date-fns doesn't accept strings as date arguments. Please use `parseISO` to parse strings. See: https://github.com/date-fns/date-fns/blob/master/docs/upgradeGuide.md#string-arguments"),
            console.warn((new Error).stack)),
            new Date(NaN))
        }
        function s(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = a(e);
            return isNaN(r) ? new Date(NaN) : r ? (n.setDate(n.getDate() + r),
            n) : n
        }
        function l(t, e) {
            o(2, arguments);
            var n = u(t).getTime()
              , r = a(e);
            return new Date(n + r)
        }
        function c(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = a(e);
            if (isNaN(r))
                return new Date(NaN);
            if (!r)
                return n;
            var i = n.getDate()
              , s = new Date(n.getTime());
            return s.setMonth(n.getMonth() + r + 1, 0),
            i >= s.getDate() ? s : (n.setFullYear(s.getFullYear(), s.getMonth(), i),
            n)
        }
        function d(t, e) {
            return o(2, arguments),
            c(t, 12 * a(e))
        }
        function h(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = u(e)
              , a = n.getTime() - r.getTime();
            return a < 0 ? -1 : a > 0 ? 1 : a
        }
        function f(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = u(e)
              , a = h(n, r)
              , i = Math.abs(function(t, e) {
                o(2, arguments);
                var n = u(t)
                  , r = u(e);
                return n.getFullYear() - r.getFullYear()
            }(n, r));
            n.setFullYear(1584),
            r.setFullYear(1584);
            var s = h(n, r) === -a
              , l = a * (i - Number(s));
            return 0 === l ? 0 : l
        }
        function v(t) {
            o(1, arguments);
            var e = u(t);
            return e.setHours(23, 59, 59, 999),
            e
        }
        function m(t) {
            o(1, arguments);
            var e = u(t)
              , n = e.getMonth();
            return e.setFullYear(e.getFullYear(), n + 1, 0),
            e.setHours(23, 59, 59, 999),
            e
        }
        function g(t, e) {
            o(2, arguments);
            var n, r = u(t), a = u(e), i = h(r, a), s = Math.abs(function(t, e) {
                o(2, arguments);
                var n = u(t)
                  , r = u(e);
                return 12 * (n.getFullYear() - r.getFullYear()) + (n.getMonth() - r.getMonth())
            }(r, a));
            if (s < 1)
                n = 0;
            else {
                1 === r.getMonth() && r.getDate() > 27 && r.setDate(30),
                r.setMonth(r.getMonth() - i * s);
                var l = h(r, a) === -i;
                (function(t) {
                    o(1, arguments);
                    var e = u(t);
                    return v(e).getTime() === m(e).getTime()
                }
                )(u(t)) && 1 === s && 1 === h(t, a) && (l = !1),
                n = i * (s - Number(l))
            }
            return 0 === n ? 0 : n
        }
        var y = {
            ceil: Math.ceil,
            round: Math.round,
            floor: Math.floor,
            trunc: function(t) {
                return t < 0 ? Math.ceil(t) : Math.floor(t)
            }
        }
          , w = "trunc";
        function p(t) {
            return t ? y[t] : y[w]
        }
        function T(t) {
            var e = new Date(Date.UTC(t.getFullYear(), t.getMonth(), t.getDate(), t.getHours(), t.getMinutes(), t.getSeconds(), t.getMilliseconds()));
            return e.setUTCFullYear(t.getFullYear()),
            t.getTime() - e.getTime()
        }
        function b(t) {
            o(1, arguments);
            var e = u(t);
            return e.setHours(0, 0, 0, 0),
            e
        }
        var k = 864e5;
        function D(t, e) {
            var n = t.getFullYear() - e.getFullYear() || t.getMonth() - e.getMonth() || t.getDate() - e.getDate() || t.getHours() - e.getHours() || t.getMinutes() - e.getMinutes() || t.getSeconds() - e.getSeconds() || t.getMilliseconds() - e.getMilliseconds();
            return n < 0 ? -1 : n > 0 ? 1 : n
        }
        function M(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = u(e)
              , a = D(n, r)
              , i = Math.abs(function(t, e) {
                o(2, arguments);
                var n = b(t)
                  , r = b(e)
                  , a = n.getTime() - T(n)
                  , i = r.getTime() - T(r);
                return Math.round((a - i) / k)
            }(n, r));
            n.setDate(n.getDate() - a * i);
            var s = a * (i - Number(D(n, r) === -a));
            return 0 === s ? 0 : s
        }
        Math.pow(10, 8);
        var C = 6e4
          , x = 36e5;
        function U(t, e) {
            return o(2, arguments),
            u(t).getTime() - u(e).getTime()
        }
        var A = {};
        function S() {
            return A
        }
        function P(t, e) {
            var n, r, i, s, l, c, d, h;
            o(1, arguments);
            var f = S()
              , v = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.weekStartsOn) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.weekStartsOn) && void 0 !== i ? i : f.weekStartsOn) && void 0 !== r ? r : null === (d = f.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.weekStartsOn) && void 0 !== n ? n : 0);
            if (!(v >= 0 && v <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            var m = u(t)
              , g = m.getDay()
              , y = 6 + (g < v ? -7 : 0) - (g - v);
            return m.setDate(m.getDate() + y),
            m.setHours(23, 59, 59, 999),
            m
        }
        function Y(t) {
            o(1, arguments);
            var e = u(t)
              , n = e.getFullYear();
            return e.setFullYear(n + 1, 0, 0),
            e.setHours(23, 59, 59, 999),
            e
        }
        function N(t) {
            if (o(1, arguments),
            !function(t) {
                return o(1, arguments),
                t instanceof Date || "object" === i(t) && "[object Date]" === Object.prototype.toString.call(t)
            }(t) && "number" !== typeof t)
                return !1;
            var e = u(t);
            return !isNaN(Number(e))
        }
        function E(t, e) {
            return o(2, arguments),
            l(t, -a(e))
        }
        function H(t) {
            o(1, arguments);
            var e = u(t)
              , n = e.getUTCDay()
              , r = (n < 1 ? 7 : 0) + n - 1;
            return e.setUTCDate(e.getUTCDate() - r),
            e.setUTCHours(0, 0, 0, 0),
            e
        }
        function O(t) {
            o(1, arguments);
            var e = u(t)
              , n = e.getUTCFullYear()
              , r = new Date(0);
            r.setUTCFullYear(n + 1, 0, 4),
            r.setUTCHours(0, 0, 0, 0);
            var a = H(r)
              , i = new Date(0);
            i.setUTCFullYear(n, 0, 4),
            i.setUTCHours(0, 0, 0, 0);
            var s = H(i);
            return e.getTime() >= a.getTime() ? n + 1 : e.getTime() >= s.getTime() ? n : n - 1
        }
        var W = 6048e5;
        function L(t) {
            o(1, arguments);
            var e = u(t)
              , n = H(e).getTime() - function(t) {
                o(1, arguments);
                var e = O(t)
                  , n = new Date(0);
                return n.setUTCFullYear(e, 0, 4),
                n.setUTCHours(0, 0, 0, 0),
                H(n)
            }(e).getTime();
            return Math.round(n / W) + 1
        }
        function F(t, e) {
            var n, r, i, s, l, c, d, h;
            o(1, arguments);
            var f = S()
              , v = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.weekStartsOn) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.weekStartsOn) && void 0 !== i ? i : f.weekStartsOn) && void 0 !== r ? r : null === (d = f.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.weekStartsOn) && void 0 !== n ? n : 0);
            if (!(v >= 0 && v <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            var m = u(t)
              , g = m.getUTCDay()
              , y = (g < v ? 7 : 0) + g - v;
            return m.setUTCDate(m.getUTCDate() - y),
            m.setUTCHours(0, 0, 0, 0),
            m
        }
        function q(t, e) {
            var n, r, i, s, l, c, d, h;
            o(1, arguments);
            var f = u(t)
              , v = f.getUTCFullYear()
              , m = S()
              , g = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.firstWeekContainsDate) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.firstWeekContainsDate) && void 0 !== i ? i : m.firstWeekContainsDate) && void 0 !== r ? r : null === (d = m.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.firstWeekContainsDate) && void 0 !== n ? n : 1);
            if (!(g >= 1 && g <= 7))
                throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
            var y = new Date(0);
            y.setUTCFullYear(v + 1, 0, g),
            y.setUTCHours(0, 0, 0, 0);
            var w = F(y, e)
              , p = new Date(0);
            p.setUTCFullYear(v, 0, g),
            p.setUTCHours(0, 0, 0, 0);
            var T = F(p, e);
            return f.getTime() >= w.getTime() ? v + 1 : f.getTime() >= T.getTime() ? v : v - 1
        }
        var R = 6048e5;
        function I(t, e) {
            o(1, arguments);
            var n = u(t)
              , r = F(n, e).getTime() - function(t, e) {
                var n, r, i, u, s, l, c, d;
                o(1, arguments);
                var h = S()
                  , f = a(null !== (n = null !== (r = null !== (i = null !== (u = null === e || void 0 === e ? void 0 : e.firstWeekContainsDate) && void 0 !== u ? u : null === e || void 0 === e || null === (s = e.locale) || void 0 === s || null === (l = s.options) || void 0 === l ? void 0 : l.firstWeekContainsDate) && void 0 !== i ? i : h.firstWeekContainsDate) && void 0 !== r ? r : null === (c = h.locale) || void 0 === c || null === (d = c.options) || void 0 === d ? void 0 : d.firstWeekContainsDate) && void 0 !== n ? n : 1)
                  , v = q(t, e)
                  , m = new Date(0);
                return m.setUTCFullYear(v, 0, f),
                m.setUTCHours(0, 0, 0, 0),
                F(m, e)
            }(n, e).getTime();
            return Math.round(r / R) + 1
        }
        function j(t, e) {
            for (var n = t < 0 ? "-" : "", r = Math.abs(t).toString(); r.length < e; )
                r = "0" + r;
            return n + r
        }
        const Q = {
            y: function(t, e) {
                var n = t.getUTCFullYear()
                  , r = n > 0 ? n : 1 - n;
                return j("yy" === e ? r % 100 : r, e.length)
            },
            M: function(t, e) {
                var n = t.getUTCMonth();
                return "M" === e ? String(n + 1) : j(n + 1, 2)
            },
            d: function(t, e) {
                return j(t.getUTCDate(), e.length)
            },
            a: function(t, e) {
                var n = t.getUTCHours() / 12 >= 1 ? "pm" : "am";
                switch (e) {
                case "a":
                case "aa":
                    return n.toUpperCase();
                case "aaa":
                    return n;
                case "aaaaa":
                    return n[0];
                default:
                    return "am" === n ? "a.m." : "p.m."
                }
            },
            h: function(t, e) {
                return j(t.getUTCHours() % 12 || 12, e.length)
            },
            H: function(t, e) {
                return j(t.getUTCHours(), e.length)
            },
            m: function(t, e) {
                return j(t.getUTCMinutes(), e.length)
            },
            s: function(t, e) {
                return j(t.getUTCSeconds(), e.length)
            },
            S: function(t, e) {
                var n = e.length
                  , r = t.getUTCMilliseconds();
                return j(Math.floor(r * Math.pow(10, n - 3)), e.length)
            }
        };
        var B = "midnight"
          , z = "noon"
          , G = "morning"
          , X = "afternoon"
          , _ = "evening"
          , Z = "night"
          , $ = {
            G: function(t, e, n) {
                var r = t.getUTCFullYear() > 0 ? 1 : 0;
                switch (e) {
                case "G":
                case "GG":
                case "GGG":
                    return n.era(r, {
                        width: "abbreviated"
                    });
                case "GGGGG":
                    return n.era(r, {
                        width: "narrow"
                    });
                default:
                    return n.era(r, {
                        width: "wide"
                    })
                }
            },
            y: function(t, e, n) {
                if ("yo" === e) {
                    var r = t.getUTCFullYear()
                      , a = r > 0 ? r : 1 - r;
                    return n.ordinalNumber(a, {
                        unit: "year"
                    })
                }
                return Q.y(t, e)
            },
            Y: function(t, e, n, r) {
                var a = q(t, r)
                  , i = a > 0 ? a : 1 - a;
                return "YY" === e ? j(i % 100, 2) : "Yo" === e ? n.ordinalNumber(i, {
                    unit: "year"
                }) : j(i, e.length)
            },
            R: function(t, e) {
                return j(O(t), e.length)
            },
            u: function(t, e) {
                return j(t.getUTCFullYear(), e.length)
            },
            Q: function(t, e, n) {
                var r = Math.ceil((t.getUTCMonth() + 1) / 3);
                switch (e) {
                case "Q":
                    return String(r);
                case "QQ":
                    return j(r, 2);
                case "Qo":
                    return n.ordinalNumber(r, {
                        unit: "quarter"
                    });
                case "QQQ":
                    return n.quarter(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "QQQQQ":
                    return n.quarter(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                default:
                    return n.quarter(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            q: function(t, e, n) {
                var r = Math.ceil((t.getUTCMonth() + 1) / 3);
                switch (e) {
                case "q":
                    return String(r);
                case "qq":
                    return j(r, 2);
                case "qo":
                    return n.ordinalNumber(r, {
                        unit: "quarter"
                    });
                case "qqq":
                    return n.quarter(r, {
                        width: "abbreviated",
                        context: "standalone"
                    });
                case "qqqqq":
                    return n.quarter(r, {
                        width: "narrow",
                        context: "standalone"
                    });
                default:
                    return n.quarter(r, {
                        width: "wide",
                        context: "standalone"
                    })
                }
            },
            M: function(t, e, n) {
                var r = t.getUTCMonth();
                switch (e) {
                case "M":
                case "MM":
                    return Q.M(t, e);
                case "Mo":
                    return n.ordinalNumber(r + 1, {
                        unit: "month"
                    });
                case "MMM":
                    return n.month(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "MMMMM":
                    return n.month(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                default:
                    return n.month(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            L: function(t, e, n) {
                var r = t.getUTCMonth();
                switch (e) {
                case "L":
                    return String(r + 1);
                case "LL":
                    return j(r + 1, 2);
                case "Lo":
                    return n.ordinalNumber(r + 1, {
                        unit: "month"
                    });
                case "LLL":
                    return n.month(r, {
                        width: "abbreviated",
                        context: "standalone"
                    });
                case "LLLLL":
                    return n.month(r, {
                        width: "narrow",
                        context: "standalone"
                    });
                default:
                    return n.month(r, {
                        width: "wide",
                        context: "standalone"
                    })
                }
            },
            w: function(t, e, n, r) {
                var a = I(t, r);
                return "wo" === e ? n.ordinalNumber(a, {
                    unit: "week"
                }) : j(a, e.length)
            },
            I: function(t, e, n) {
                var r = L(t);
                return "Io" === e ? n.ordinalNumber(r, {
                    unit: "week"
                }) : j(r, e.length)
            },
            d: function(t, e, n) {
                return "do" === e ? n.ordinalNumber(t.getUTCDate(), {
                    unit: "date"
                }) : Q.d(t, e)
            },
            D: function(t, e, n) {
                var r = function(t) {
                    o(1, arguments);
                    var e = u(t)
                      , n = e.getTime();
                    e.setUTCMonth(0, 1),
                    e.setUTCHours(0, 0, 0, 0);
                    var r = n - e.getTime();
                    return Math.floor(r / 864e5) + 1
                }(t);
                return "Do" === e ? n.ordinalNumber(r, {
                    unit: "dayOfYear"
                }) : j(r, e.length)
            },
            E: function(t, e, n) {
                var r = t.getUTCDay();
                switch (e) {
                case "E":
                case "EE":
                case "EEE":
                    return n.day(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "EEEEE":
                    return n.day(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                case "EEEEEE":
                    return n.day(r, {
                        width: "short",
                        context: "formatting"
                    });
                default:
                    return n.day(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            e: function(t, e, n, r) {
                var a = t.getUTCDay()
                  , i = (a - r.weekStartsOn + 8) % 7 || 7;
                switch (e) {
                case "e":
                    return String(i);
                case "ee":
                    return j(i, 2);
                case "eo":
                    return n.ordinalNumber(i, {
                        unit: "day"
                    });
                case "eee":
                    return n.day(a, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "eeeee":
                    return n.day(a, {
                        width: "narrow",
                        context: "formatting"
                    });
                case "eeeeee":
                    return n.day(a, {
                        width: "short",
                        context: "formatting"
                    });
                default:
                    return n.day(a, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            c: function(t, e, n, r) {
                var a = t.getUTCDay()
                  , i = (a - r.weekStartsOn + 8) % 7 || 7;
                switch (e) {
                case "c":
                    return String(i);
                case "cc":
                    return j(i, e.length);
                case "co":
                    return n.ordinalNumber(i, {
                        unit: "day"
                    });
                case "ccc":
                    return n.day(a, {
                        width: "abbreviated",
                        context: "standalone"
                    });
                case "ccccc":
                    return n.day(a, {
                        width: "narrow",
                        context: "standalone"
                    });
                case "cccccc":
                    return n.day(a, {
                        width: "short",
                        context: "standalone"
                    });
                default:
                    return n.day(a, {
                        width: "wide",
                        context: "standalone"
                    })
                }
            },
            i: function(t, e, n) {
                var r = t.getUTCDay()
                  , a = 0 === r ? 7 : r;
                switch (e) {
                case "i":
                    return String(a);
                case "ii":
                    return j(a, e.length);
                case "io":
                    return n.ordinalNumber(a, {
                        unit: "day"
                    });
                case "iii":
                    return n.day(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "iiiii":
                    return n.day(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                case "iiiiii":
                    return n.day(r, {
                        width: "short",
                        context: "formatting"
                    });
                default:
                    return n.day(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            a: function(t, e, n) {
                var r = t.getUTCHours() / 12 >= 1 ? "pm" : "am";
                switch (e) {
                case "a":
                case "aa":
                    return n.dayPeriod(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "aaa":
                    return n.dayPeriod(r, {
                        width: "abbreviated",
                        context: "formatting"
                    }).toLowerCase();
                case "aaaaa":
                    return n.dayPeriod(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                default:
                    return n.dayPeriod(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            b: function(t, e, n) {
                var r, a = t.getUTCHours();
                switch (r = 12 === a ? z : 0 === a ? B : a / 12 >= 1 ? "pm" : "am",
                e) {
                case "b":
                case "bb":
                    return n.dayPeriod(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "bbb":
                    return n.dayPeriod(r, {
                        width: "abbreviated",
                        context: "formatting"
                    }).toLowerCase();
                case "bbbbb":
                    return n.dayPeriod(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                default:
                    return n.dayPeriod(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            B: function(t, e, n) {
                var r, a = t.getUTCHours();
                switch (r = a >= 17 ? _ : a >= 12 ? X : a >= 4 ? G : Z,
                e) {
                case "B":
                case "BB":
                case "BBB":
                    return n.dayPeriod(r, {
                        width: "abbreviated",
                        context: "formatting"
                    });
                case "BBBBB":
                    return n.dayPeriod(r, {
                        width: "narrow",
                        context: "formatting"
                    });
                default:
                    return n.dayPeriod(r, {
                        width: "wide",
                        context: "formatting"
                    })
                }
            },
            h: function(t, e, n) {
                if ("ho" === e) {
                    var r = t.getUTCHours() % 12;
                    return 0 === r && (r = 12),
                    n.ordinalNumber(r, {
                        unit: "hour"
                    })
                }
                return Q.h(t, e)
            },
            H: function(t, e, n) {
                return "Ho" === e ? n.ordinalNumber(t.getUTCHours(), {
                    unit: "hour"
                }) : Q.H(t, e)
            },
            K: function(t, e, n) {
                var r = t.getUTCHours() % 12;
                return "Ko" === e ? n.ordinalNumber(r, {
                    unit: "hour"
                }) : j(r, e.length)
            },
            k: function(t, e, n) {
                var r = t.getUTCHours();
                return 0 === r && (r = 24),
                "ko" === e ? n.ordinalNumber(r, {
                    unit: "hour"
                }) : j(r, e.length)
            },
            m: function(t, e, n) {
                return "mo" === e ? n.ordinalNumber(t.getUTCMinutes(), {
                    unit: "minute"
                }) : Q.m(t, e)
            },
            s: function(t, e, n) {
                return "so" === e ? n.ordinalNumber(t.getUTCSeconds(), {
                    unit: "second"
                }) : Q.s(t, e)
            },
            S: function(t, e) {
                return Q.S(t, e)
            },
            X: function(t, e, n, r) {
                var a = (r._originalDate || t).getTimezoneOffset();
                if (0 === a)
                    return "Z";
                switch (e) {
                case "X":
                    return K(a);
                case "XXXX":
                case "XX":
                    return V(a);
                default:
                    return V(a, ":")
                }
            },
            x: function(t, e, n, r) {
                var a = (r._originalDate || t).getTimezoneOffset();
                switch (e) {
                case "x":
                    return K(a);
                case "xxxx":
                case "xx":
                    return V(a);
                default:
                    return V(a, ":")
                }
            },
            O: function(t, e, n, r) {
                var a = (r._originalDate || t).getTimezoneOffset();
                switch (e) {
                case "O":
                case "OO":
                case "OOO":
                    return "GMT" + J(a, ":");
                default:
                    return "GMT" + V(a, ":")
                }
            },
            z: function(t, e, n, r) {
                var a = (r._originalDate || t).getTimezoneOffset();
                switch (e) {
                case "z":
                case "zz":
                case "zzz":
                    return "GMT" + J(a, ":");
                default:
                    return "GMT" + V(a, ":")
                }
            },
            t: function(t, e, n, r) {
                var a = r._originalDate || t;
                return j(Math.floor(a.getTime() / 1e3), e.length)
            },
            T: function(t, e, n, r) {
                return j((r._originalDate || t).getTime(), e.length)
            }
        };
        function J(t, e) {
            var n = t > 0 ? "-" : "+"
              , r = Math.abs(t)
              , a = Math.floor(r / 60)
              , i = r % 60;
            if (0 === i)
                return n + String(a);
            var o = e || "";
            return n + String(a) + o + j(i, 2)
        }
        function K(t, e) {
            return t % 60 === 0 ? (t > 0 ? "-" : "+") + j(Math.abs(t) / 60, 2) : V(t, e)
        }
        function V(t, e) {
            var n = e || ""
              , r = t > 0 ? "-" : "+"
              , a = Math.abs(t);
            return r + j(Math.floor(a / 60), 2) + n + j(a % 60, 2)
        }
        const tt = $;
        var et = function(t, e) {
            switch (t) {
            case "P":
                return e.date({
                    width: "short"
                });
            case "PP":
                return e.date({
                    width: "medium"
                });
            case "PPP":
                return e.date({
                    width: "long"
                });
            default:
                return e.date({
                    width: "full"
                })
            }
        }
          , nt = function(t, e) {
            switch (t) {
            case "p":
                return e.time({
                    width: "short"
                });
            case "pp":
                return e.time({
                    width: "medium"
                });
            case "ppp":
                return e.time({
                    width: "long"
                });
            default:
                return e.time({
                    width: "full"
                })
            }
        }
          , rt = {
            p: nt,
            P: function(t, e) {
                var n, r = t.match(/(P+)(p+)?/) || [], a = r[1], i = r[2];
                if (!i)
                    return et(t, e);
                switch (a) {
                case "P":
                    n = e.dateTime({
                        width: "short"
                    });
                    break;
                case "PP":
                    n = e.dateTime({
                        width: "medium"
                    });
                    break;
                case "PPP":
                    n = e.dateTime({
                        width: "long"
                    });
                    break;
                default:
                    n = e.dateTime({
                        width: "full"
                    })
                }
                return n.replace("{{date}}", et(a, e)).replace("{{time}}", nt(i, e))
            }
        };
        const at = rt;
        var it = ["D", "DD"]
          , ot = ["YY", "YYYY"];
        function ut(t) {
            return -1 !== it.indexOf(t)
        }
        function st(t) {
            return -1 !== ot.indexOf(t)
        }
        function lt(t, e, n) {
            if ("YYYY" === t)
                throw new RangeError("Use `yyyy` instead of `YYYY` (in `".concat(e, "`) for formatting years to the input `").concat(n, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
            if ("YY" === t)
                throw new RangeError("Use `yy` instead of `YY` (in `".concat(e, "`) for formatting years to the input `").concat(n, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
            if ("D" === t)
                throw new RangeError("Use `d` instead of `D` (in `".concat(e, "`) for formatting days of the month to the input `").concat(n, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
            if ("DD" === t)
                throw new RangeError("Use `dd` instead of `DD` (in `".concat(e, "`) for formatting days of the month to the input `").concat(n, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"))
        }
        var ct = {
            lessThanXSeconds: {
                one: "less than a second",
                other: "less than {{count}} seconds"
            },
            xSeconds: {
                one: "1 second",
                other: "{{count}} seconds"
            },
            halfAMinute: "half a minute",
            lessThanXMinutes: {
                one: "less than a minute",
                other: "less than {{count}} minutes"
            },
            xMinutes: {
                one: "1 minute",
                other: "{{count}} minutes"
            },
            aboutXHours: {
                one: "about 1 hour",
                other: "about {{count}} hours"
            },
            xHours: {
                one: "1 hour",
                other: "{{count}} hours"
            },
            xDays: {
                one: "1 day",
                other: "{{count}} days"
            },
            aboutXWeeks: {
                one: "about 1 week",
                other: "about {{count}} weeks"
            },
            xWeeks: {
                one: "1 week",
                other: "{{count}} weeks"
            },
            aboutXMonths: {
                one: "about 1 month",
                other: "about {{count}} months"
            },
            xMonths: {
                one: "1 month",
                other: "{{count}} months"
            },
            aboutXYears: {
                one: "about 1 year",
                other: "about {{count}} years"
            },
            xYears: {
                one: "1 year",
                other: "{{count}} years"
            },
            overXYears: {
                one: "over 1 year",
                other: "over {{count}} years"
            },
            almostXYears: {
                one: "almost 1 year",
                other: "almost {{count}} years"
            }
        };
        const dt = function(t, e, n) {
            var r, a = ct[t];
            return r = "string" === typeof a ? a : 1 === e ? a.one : a.other.replace("{{count}}", e.toString()),
            null !== n && void 0 !== n && n.addSuffix ? n.comparison && n.comparison > 0 ? "in " + r : r + " ago" : r
        };
        function ht(t) {
            return function() {
                var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
                  , n = e.width ? String(e.width) : t.defaultWidth;
                return t.formats[n] || t.formats[t.defaultWidth]
            }
        }
        var ft = {
            date: ht({
                formats: {
                    full: "EEEE, MMMM do, y",
                    long: "MMMM do, y",
                    medium: "MMM d, y",
                    short: "MM/dd/yyyy"
                },
                defaultWidth: "full"
            }),
            time: ht({
                formats: {
                    full: "h:mm:ss a zzzz",
                    long: "h:mm:ss a z",
                    medium: "h:mm:ss a",
                    short: "h:mm a"
                },
                defaultWidth: "full"
            }),
            dateTime: ht({
                formats: {
                    full: "{{date}} 'at' {{time}}",
                    long: "{{date}} 'at' {{time}}",
                    medium: "{{date}}, {{time}}",
                    short: "{{date}}, {{time}}"
                },
                defaultWidth: "full"
            })
        };
        var vt = {
            lastWeek: "'last' eeee 'at' p",
            yesterday: "'yesterday at' p",
            today: "'today at' p",
            tomorrow: "'tomorrow at' p",
            nextWeek: "eeee 'at' p",
            other: "P"
        };
        function mt(t) {
            return function(e, n) {
                var r;
                if ("formatting" === (null !== n && void 0 !== n && n.context ? String(n.context) : "standalone") && t.formattingValues) {
                    var a = t.defaultFormattingWidth || t.defaultWidth
                      , i = null !== n && void 0 !== n && n.width ? String(n.width) : a;
                    r = t.formattingValues[i] || t.formattingValues[a]
                } else {
                    var o = t.defaultWidth
                      , u = null !== n && void 0 !== n && n.width ? String(n.width) : t.defaultWidth;
                    r = t.values[u] || t.values[o]
                }
                return r[t.argumentCallback ? t.argumentCallback(e) : e]
            }
        }
        function gt(t) {
            return function(e) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {}
                  , r = n.width
                  , a = r && t.matchPatterns[r] || t.matchPatterns[t.defaultMatchWidth]
                  , i = e.match(a);
                if (!i)
                    return null;
                var o, u = i[0], s = r && t.parsePatterns[r] || t.parsePatterns[t.defaultParseWidth], l = Array.isArray(s) ? function(t, e) {
                    for (var n = 0; n < t.length; n++)
                        if (e(t[n]))
                            return n;
                    return
                }(s, (function(t) {
                    return t.test(u)
                }
                )) : function(t, e) {
                    for (var n in t)
                        if (t.hasOwnProperty(n) && e(t[n]))
                            return n;
                    return
                }(s, (function(t) {
                    return t.test(u)
                }
                ));
                return o = t.valueCallback ? t.valueCallback(l) : l,
                {
                    value: o = n.valueCallback ? n.valueCallback(o) : o,
                    rest: e.slice(u.length)
                }
            }
        }
        var yt;
        const wt = {
            code: "en-US",
            formatDistance: dt,
            formatLong: ft,
            formatRelative: function(t, e, n, r) {
                return vt[t]
            },
            localize: {
                ordinalNumber: function(t, e) {
                    var n = Number(t)
                      , r = n % 100;
                    if (r > 20 || r < 10)
                        switch (r % 10) {
                        case 1:
                            return n + "st";
                        case 2:
                            return n + "nd";
                        case 3:
                            return n + "rd"
                        }
                    return n + "th"
                },
                era: mt({
                    values: {
                        narrow: ["B", "A"],
                        abbreviated: ["BC", "AD"],
                        wide: ["Before Christ", "Anno Domini"]
                    },
                    defaultWidth: "wide"
                }),
                quarter: mt({
                    values: {
                        narrow: ["1", "2", "3", "4"],
                        abbreviated: ["Q1", "Q2", "Q3", "Q4"],
                        wide: ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]
                    },
                    defaultWidth: "wide",
                    argumentCallback: function(t) {
                        return t - 1
                    }
                }),
                month: mt({
                    values: {
                        narrow: ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
                        abbreviated: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                        wide: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    },
                    defaultWidth: "wide"
                }),
                day: mt({
                    values: {
                        narrow: ["S", "M", "T", "W", "T", "F", "S"],
                        short: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
                        abbreviated: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                        wide: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                    },
                    defaultWidth: "wide"
                }),
                dayPeriod: mt({
                    values: {
                        narrow: {
                            am: "a",
                            pm: "p",
                            midnight: "mi",
                            noon: "n",
                            morning: "morning",
                            afternoon: "afternoon",
                            evening: "evening",
                            night: "night"
                        },
                        abbreviated: {
                            am: "AM",
                            pm: "PM",
                            midnight: "midnight",
                            noon: "noon",
                            morning: "morning",
                            afternoon: "afternoon",
                            evening: "evening",
                            night: "night"
                        },
                        wide: {
                            am: "a.m.",
                            pm: "p.m.",
                            midnight: "midnight",
                            noon: "noon",
                            morning: "morning",
                            afternoon: "afternoon",
                            evening: "evening",
                            night: "night"
                        }
                    },
                    defaultWidth: "wide",
                    formattingValues: {
                        narrow: {
                            am: "a",
                            pm: "p",
                            midnight: "mi",
                            noon: "n",
                            morning: "in the morning",
                            afternoon: "in the afternoon",
                            evening: "in the evening",
                            night: "at night"
                        },
                        abbreviated: {
                            am: "AM",
                            pm: "PM",
                            midnight: "midnight",
                            noon: "noon",
                            morning: "in the morning",
                            afternoon: "in the afternoon",
                            evening: "in the evening",
                            night: "at night"
                        },
                        wide: {
                            am: "a.m.",
                            pm: "p.m.",
                            midnight: "midnight",
                            noon: "noon",
                            morning: "in the morning",
                            afternoon: "in the afternoon",
                            evening: "in the evening",
                            night: "at night"
                        }
                    },
                    defaultFormattingWidth: "wide"
                })
            },
            match: {
                ordinalNumber: (yt = {
                    matchPattern: /^(\d+)(th|st|nd|rd)?/i,
                    parsePattern: /\d+/i,
                    valueCallback: function(t) {
                        return parseInt(t, 10)
                    }
                },
                function(t) {
                    var e = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {}
                      , n = t.match(yt.matchPattern);
                    if (!n)
                        return null;
                    var r = n[0]
                      , a = t.match(yt.parsePattern);
                    if (!a)
                        return null;
                    var i = yt.valueCallback ? yt.valueCallback(a[0]) : a[0];
                    return {
                        value: i = e.valueCallback ? e.valueCallback(i) : i,
                        rest: t.slice(r.length)
                    }
                }
                ),
                era: gt({
                    matchPatterns: {
                        narrow: /^(b|a)/i,
                        abbreviated: /^(b\.?\s?c\.?|b\.?\s?c\.?\s?e\.?|a\.?\s?d\.?|c\.?\s?e\.?)/i,
                        wide: /^(before christ|before common era|anno domini|common era)/i
                    },
                    defaultMatchWidth: "wide",
                    parsePatterns: {
                        any: [/^b/i, /^(a|c)/i]
                    },
                    defaultParseWidth: "any"
                }),
                quarter: gt({
                    matchPatterns: {
                        narrow: /^[1234]/i,
                        abbreviated: /^q[1234]/i,
                        wide: /^[1234](th|st|nd|rd)? quarter/i
                    },
                    defaultMatchWidth: "wide",
                    parsePatterns: {
                        any: [/1/i, /2/i, /3/i, /4/i]
                    },
                    defaultParseWidth: "any",
                    valueCallback: function(t) {
                        return t + 1
                    }
                }),
                month: gt({
                    matchPatterns: {
                        narrow: /^[jfmasond]/i,
                        abbreviated: /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
                        wide: /^(january|february|march|april|may|june|july|august|september|october|november|december)/i
                    },
                    defaultMatchWidth: "wide",
                    parsePatterns: {
                        narrow: [/^j/i, /^f/i, /^m/i, /^a/i, /^m/i, /^j/i, /^j/i, /^a/i, /^s/i, /^o/i, /^n/i, /^d/i],
                        any: [/^ja/i, /^f/i, /^mar/i, /^ap/i, /^may/i, /^jun/i, /^jul/i, /^au/i, /^s/i, /^o/i, /^n/i, /^d/i]
                    },
                    defaultParseWidth: "any"
                }),
                day: gt({
                    matchPatterns: {
                        narrow: /^[smtwf]/i,
                        short: /^(su|mo|tu|we|th|fr|sa)/i,
                        abbreviated: /^(sun|mon|tue|wed|thu|fri|sat)/i,
                        wide: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
                    },
                    defaultMatchWidth: "wide",
                    parsePatterns: {
                        narrow: [/^s/i, /^m/i, /^t/i, /^w/i, /^t/i, /^f/i, /^s/i],
                        any: [/^su/i, /^m/i, /^tu/i, /^w/i, /^th/i, /^f/i, /^sa/i]
                    },
                    defaultParseWidth: "any"
                }),
                dayPeriod: gt({
                    matchPatterns: {
                        narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
                        any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i
                    },
                    defaultMatchWidth: "any",
                    parsePatterns: {
                        any: {
                            am: /^a/i,
                            pm: /^p/i,
                            midnight: /^mi/i,
                            noon: /^no/i,
                            morning: /morning/i,
                            afternoon: /afternoon/i,
                            evening: /evening/i,
                            night: /night/i
                        }
                    },
                    defaultParseWidth: "any"
                })
            },
            options: {
                weekStartsOn: 0,
                firstWeekContainsDate: 1
            }
        }
          , pt = wt;
        var Tt = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g
          , bt = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g
          , kt = /^'([^]*?)'?$/
          , Dt = /''/g
          , Mt = /[a-zA-Z]/;
        function Ct(t, e, n) {
            var r, i, s, l, c, d, h, f, v, m, g, y, w, p, b, k, D, M;
            o(2, arguments);
            var C = String(e)
              , x = S()
              , U = null !== (r = null !== (i = null === n || void 0 === n ? void 0 : n.locale) && void 0 !== i ? i : x.locale) && void 0 !== r ? r : pt
              , A = a(null !== (s = null !== (l = null !== (c = null !== (d = null === n || void 0 === n ? void 0 : n.firstWeekContainsDate) && void 0 !== d ? d : null === n || void 0 === n || null === (h = n.locale) || void 0 === h || null === (f = h.options) || void 0 === f ? void 0 : f.firstWeekContainsDate) && void 0 !== c ? c : x.firstWeekContainsDate) && void 0 !== l ? l : null === (v = x.locale) || void 0 === v || null === (m = v.options) || void 0 === m ? void 0 : m.firstWeekContainsDate) && void 0 !== s ? s : 1);
            if (!(A >= 1 && A <= 7))
                throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
            var P = a(null !== (g = null !== (y = null !== (w = null !== (p = null === n || void 0 === n ? void 0 : n.weekStartsOn) && void 0 !== p ? p : null === n || void 0 === n || null === (b = n.locale) || void 0 === b || null === (k = b.options) || void 0 === k ? void 0 : k.weekStartsOn) && void 0 !== w ? w : x.weekStartsOn) && void 0 !== y ? y : null === (D = x.locale) || void 0 === D || null === (M = D.options) || void 0 === M ? void 0 : M.weekStartsOn) && void 0 !== g ? g : 0);
            if (!(P >= 0 && P <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            if (!U.localize)
                throw new RangeError("locale must contain localize property");
            if (!U.formatLong)
                throw new RangeError("locale must contain formatLong property");
            var Y = u(t);
            if (!N(Y))
                throw new RangeError("Invalid time value");
            var H = E(Y, T(Y))
              , O = {
                firstWeekContainsDate: A,
                weekStartsOn: P,
                locale: U,
                _originalDate: Y
            };
            return C.match(bt).map((function(t) {
                var e = t[0];
                return "p" === e || "P" === e ? (0,
                at[e])(t, U.formatLong) : t
            }
            )).join("").match(Tt).map((function(r) {
                if ("''" === r)
                    return "'";
                var a = r[0];
                if ("'" === a)
                    return function(t) {
                        var e = t.match(kt);
                        if (!e)
                            return t;
                        return e[1].replace(Dt, "'")
                    }(r);
                var i = tt[a];
                if (i)
                    return null !== n && void 0 !== n && n.useAdditionalWeekYearTokens || !st(r) || lt(r, e, String(t)),
                    null !== n && void 0 !== n && n.useAdditionalDayOfYearTokens || !ut(r) || lt(r, e, String(t)),
                    i(H, r, U.localize, O);
                if (a.match(Mt))
                    throw new RangeError("Format string contains an unescaped latin alphabet character `" + a + "`");
                return r
            }
            )).join("")
        }
        function xt(t) {
            o(1, arguments);
            var e = u(t)
              , n = e.getFullYear()
              , r = e.getMonth()
              , a = new Date(0);
            return a.setFullYear(n, r + 1, 0),
            a.setHours(0, 0, 0, 0),
            a.getDate()
        }
        function Ut(t, e) {
            var n, r, i, s, l, c, d, h;
            o(1, arguments);
            var f = S()
              , v = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.weekStartsOn) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.weekStartsOn) && void 0 !== i ? i : f.weekStartsOn) && void 0 !== r ? r : null === (d = f.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.weekStartsOn) && void 0 !== n ? n : 0);
            if (!(v >= 0 && v <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            var m = u(t)
              , g = m.getDay()
              , y = (g < v ? 7 : 0) + g - v;
            return m.setDate(m.getDate() - y),
            m.setHours(0, 0, 0, 0),
            m
        }
        function At(t, e) {
            var n, r, i, s, l, c, d, h;
            o(1, arguments);
            var f = S()
              , v = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.firstWeekContainsDate) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.firstWeekContainsDate) && void 0 !== i ? i : f.firstWeekContainsDate) && void 0 !== r ? r : null === (d = f.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.firstWeekContainsDate) && void 0 !== n ? n : 1)
              , m = function(t, e) {
                var n, r, i, s, l, c, d, h;
                o(1, arguments);
                var f = u(t)
                  , v = f.getFullYear()
                  , m = S()
                  , g = a(null !== (n = null !== (r = null !== (i = null !== (s = null === e || void 0 === e ? void 0 : e.firstWeekContainsDate) && void 0 !== s ? s : null === e || void 0 === e || null === (l = e.locale) || void 0 === l || null === (c = l.options) || void 0 === c ? void 0 : c.firstWeekContainsDate) && void 0 !== i ? i : m.firstWeekContainsDate) && void 0 !== r ? r : null === (d = m.locale) || void 0 === d || null === (h = d.options) || void 0 === h ? void 0 : h.firstWeekContainsDate) && void 0 !== n ? n : 1);
                if (!(g >= 1 && g <= 7))
                    throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
                var y = new Date(0);
                y.setFullYear(v + 1, 0, g),
                y.setHours(0, 0, 0, 0);
                var w = Ut(y, e)
                  , p = new Date(0);
                p.setFullYear(v, 0, g),
                p.setHours(0, 0, 0, 0);
                var T = Ut(p, e);
                return f.getTime() >= w.getTime() ? v + 1 : f.getTime() >= T.getTime() ? v : v - 1
            }(t, e)
              , g = new Date(0);
            return g.setFullYear(m, 0, v),
            g.setHours(0, 0, 0, 0),
            Ut(g, e)
        }
        function St(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = u(e);
            return n.getTime() > r.getTime()
        }
        function Pt(t, e) {
            o(2, arguments);
            var n = u(t)
              , r = u(e);
            return n.getTime() < r.getTime()
        }
        function Yt(t) {
            o(1, arguments);
            var e = u(t);
            return e.setMinutes(0, 0, 0),
            e
        }
        function Nt(t, e) {
            (null == e || e > t.length) && (e = t.length);
            for (var n = 0, r = Array(e); n < e; n++)
                r[n] = t[n];
            return r
        }
        function Et(t, e) {
            var n = "undefined" != typeof Symbol && t[Symbol.iterator] || t["@@iterator"];
            if (!n) {
                if (Array.isArray(t) || (n = function(t, e) {
                    if (t) {
                        if ("string" == typeof t)
                            return Nt(t, e);
                        var n = {}.toString.call(t).slice(8, -1);
                        return "Object" === n && t.constructor && (n = t.constructor.name),
                        "Map" === n || "Set" === n ? Array.from(t) : "Arguments" === n || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? Nt(t, e) : void 0
                    }
                }(t)) || e && t && "number" == typeof t.length) {
                    n && (t = n);
                    var r = 0
                      , a = function() {};
                    return {
                        s: a,
                        n: function() {
                            return r >= t.length ? {
                                done: !0
                            } : {
                                done: !1,
                                value: t[r++]
                            }
                        },
                        e: function(t) {
                            throw t
                        },
                        f: a
                    }
                }
                throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
            }
            var i, o = !0, u = !1;
            return {
                s: function() {
                    n = n.call(t)
                },
                n: function() {
                    var t = n.next();
                    return o = t.done,
                    t
                },
                e: function(t) {
                    u = !0,
                    i = t
                },
                f: function() {
                    try {
                        o || null == n.return || n.return()
                    } finally {
                        if (u)
                            throw i
                    }
                }
            }
        }
        function Ht(t, e) {
            if (null == t)
                throw new TypeError("assign requires that input parameter not be null or undefined");
            for (var n in e)
                Object.prototype.hasOwnProperty.call(e, n) && (t[n] = e[n]);
            return t
        }
        var Ot = n(99805)
          , Wt = n(82050);
        function Lt(t, e) {
            if ("function" != typeof e && null !== e)
                throw new TypeError("Super expression must either be null or a function");
            t.prototype = Object.create(e && e.prototype, {
                constructor: {
                    value: t,
                    writable: !0,
                    configurable: !0
                }
            }),
            Object.defineProperty(t, "prototype", {
                writable: !1
            }),
            e && (0,
            Wt.A)(t, e)
        }
        function Ft(t) {
            return Ft = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
                return t.__proto__ || Object.getPrototypeOf(t)
            }
            ,
            Ft(t)
        }
        function qt() {
            try {
                var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], (function() {}
                )))
            } catch (t) {}
            return (qt = function() {
                return !!t
            }
            )()
        }
        function Rt(t) {
            var e = qt();
            return function() {
                var n, r = Ft(t);
                if (e) {
                    var a = Ft(this).constructor;
                    n = Reflect.construct(r, arguments, a)
                } else
                    n = r.apply(this, arguments);
                return function(t, e) {
                    if (e && ("object" == i(e) || "function" == typeof e))
                        return e;
                    if (void 0 !== e)
                        throw new TypeError("Derived constructors may only return object or undefined");
                    return (0,
                    Ot.A)(t)
                }(this, n)
            }
        }
        function It(t, e) {
            if (!(t instanceof e))
                throw new TypeError("Cannot call a class as a function")
        }
        function jt(t) {
            var e = function(t, e) {
                if ("object" != i(t) || !t)
                    return t;
                var n = t[Symbol.toPrimitive];
                if (void 0 !== n) {
                    var r = n.call(t, e || "default");
                    if ("object" != i(r))
                        return r;
                    throw new TypeError("@@toPrimitive must return a primitive value.")
                }
                return ("string" === e ? String : Number)(t)
            }(t, "string");
            return "symbol" == i(e) ? e : e + ""
        }
        function Qt(t, e) {
            for (var n = 0; n < e.length; n++) {
                var r = e[n];
                r.enumerable = r.enumerable || !1,
                r.configurable = !0,
                "value"in r && (r.writable = !0),
                Object.defineProperty(t, jt(r.key), r)
            }
        }
        function Bt(t, e, n) {
            return e && Qt(t.prototype, e),
            n && Qt(t, n),
            Object.defineProperty(t, "prototype", {
                writable: !1
            }),
            t
        }
        function zt(t, e, n) {
            return (e = jt(e))in t ? Object.defineProperty(t, e, {
                value: n,
                enumerable: !0,
                configurable: !0,
                writable: !0
            }) : t[e] = n,
            t
        }
        var Gt = function() {
            function t() {
                It(this, t),
                zt(this, "priority", void 0),
                zt(this, "subPriority", 0)
            }
            return Bt(t, [{
                key: "validate",
                value: function(t, e) {
                    return !0
                }
            }]),
            t
        }()
          , Xt = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n(t, r, a, i, o) {
                var u;
                return It(this, n),
                (u = e.call(this)).value = t,
                u.validateValue = r,
                u.setValue = a,
                u.priority = i,
                o && (u.subPriority = o),
                u
            }
            return Bt(n, [{
                key: "validate",
                value: function(t, e) {
                    return this.validateValue(t, this.value, e)
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return this.setValue(t, e, this.value, n)
                }
            }]),
            n
        }(Gt)
          , _t = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 10),
                zt((0,
                Ot.A)(t), "subPriority", -1),
                t
            }
            return Bt(n, [{
                key: "set",
                value: function(t, e) {
                    if (e.timestampIsSet)
                        return t;
                    var n = new Date(0);
                    return n.setFullYear(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate()),
                    n.setHours(t.getUTCHours(), t.getUTCMinutes(), t.getUTCSeconds(), t.getUTCMilliseconds()),
                    n
                }
            }]),
            n
        }(Gt)
          , Zt = function() {
            function t() {
                It(this, t),
                zt(this, "incompatibleTokens", void 0),
                zt(this, "priority", void 0),
                zt(this, "subPriority", void 0)
            }
            return Bt(t, [{
                key: "run",
                value: function(t, e, n, r) {
                    var a = this.parse(t, e, n, r);
                    return a ? {
                        setter: new Xt(a.value,this.validate,this.set,this.priority,this.subPriority),
                        rest: a.rest
                    } : null
                }
            }, {
                key: "validate",
                value: function(t, e, n) {
                    return !0
                }
            }]),
            t
        }()
          , $t = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 140),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["R", "u", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "G":
                    case "GG":
                    case "GGG":
                        return n.era(t, {
                            width: "abbreviated"
                        }) || n.era(t, {
                            width: "narrow"
                        });
                    case "GGGGG":
                        return n.era(t, {
                            width: "narrow"
                        });
                    default:
                        return n.era(t, {
                            width: "wide"
                        }) || n.era(t, {
                            width: "abbreviated"
                        }) || n.era(t, {
                            width: "narrow"
                        })
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return e.era = n,
                    t.setUTCFullYear(n, 0, 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Jt = /^(1[0-2]|0?\d)/
          , Kt = /^(3[0-1]|[0-2]?\d)/
          , Vt = /^(36[0-6]|3[0-5]\d|[0-2]?\d?\d)/
          , te = /^(5[0-3]|[0-4]?\d)/
          , ee = /^(2[0-3]|[0-1]?\d)/
          , ne = /^(2[0-4]|[0-1]?\d)/
          , re = /^(1[0-1]|0?\d)/
          , ae = /^(1[0-2]|0?\d)/
          , ie = /^[0-5]?\d/
          , oe = /^[0-5]?\d/
          , ue = /^\d/
          , se = /^\d{1,2}/
          , le = /^\d{1,3}/
          , ce = /^\d{1,4}/
          , de = /^-?\d+/
          , he = /^-?\d/
          , fe = /^-?\d{1,2}/
          , ve = /^-?\d{1,3}/
          , me = /^-?\d{1,4}/
          , ge = /^([+-])(\d{2})(\d{2})?|Z/
          , ye = /^([+-])(\d{2})(\d{2})|Z/
          , we = /^([+-])(\d{2})(\d{2})((\d{2}))?|Z/
          , pe = /^([+-])(\d{2}):(\d{2})|Z/
          , Te = /^([+-])(\d{2}):(\d{2})(:(\d{2}))?|Z/;
        function be(t, e) {
            return t ? {
                value: e(t.value),
                rest: t.rest
            } : t
        }
        function ke(t, e) {
            var n = e.match(t);
            return n ? {
                value: parseInt(n[0], 10),
                rest: e.slice(n[0].length)
            } : null
        }
        function De(t, e) {
            var n = e.match(t);
            if (!n)
                return null;
            if ("Z" === n[0])
                return {
                    value: 0,
                    rest: e.slice(1)
                };
            var r = "+" === n[1] ? 1 : -1
              , a = n[2] ? parseInt(n[2], 10) : 0
              , i = n[3] ? parseInt(n[3], 10) : 0
              , o = n[5] ? parseInt(n[5], 10) : 0;
            return {
                value: r * (a * x + i * C + 1e3 * o),
                rest: e.slice(n[0].length)
            }
        }
        function Me(t) {
            return ke(de, t)
        }
        function Ce(t, e) {
            switch (t) {
            case 1:
                return ke(ue, e);
            case 2:
                return ke(se, e);
            case 3:
                return ke(le, e);
            case 4:
                return ke(ce, e);
            default:
                return ke(new RegExp("^\\d{1," + t + "}"), e)
            }
        }
        function xe(t, e) {
            switch (t) {
            case 1:
                return ke(he, e);
            case 2:
                return ke(fe, e);
            case 3:
                return ke(ve, e);
            case 4:
                return ke(me, e);
            default:
                return ke(new RegExp("^-?\\d{1," + t + "}"), e)
            }
        }
        function Ue(t) {
            switch (t) {
            case "morning":
                return 4;
            case "evening":
                return 17;
            case "pm":
            case "noon":
            case "afternoon":
                return 12;
            default:
                return 0
            }
        }
        function Ae(t, e) {
            var n, r = e > 0, a = r ? e : 1 - e;
            if (a <= 50)
                n = t || 100;
            else {
                var i = a + 50;
                n = t + 100 * Math.floor(i / 100) - (t >= i % 100 ? 100 : 0)
            }
            return r ? n : 1 - n
        }
        function Se(t) {
            return t % 400 === 0 || t % 4 === 0 && t % 100 !== 0
        }
        var Pe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 130),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "u", "w", "I", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    var r = function(t) {
                        return {
                            year: t,
                            isTwoDigitYear: "yy" === e
                        }
                    };
                    switch (e) {
                    case "y":
                        return be(Ce(4, t), r);
                    case "yo":
                        return be(n.ordinalNumber(t, {
                            unit: "year"
                        }), r);
                    default:
                        return be(Ce(e.length, t), r)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e.isTwoDigitYear || e.year > 0
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    var r = t.getUTCFullYear();
                    if (n.isTwoDigitYear) {
                        var a = Ae(n.year, r);
                        return t.setUTCFullYear(a, 0, 1),
                        t.setUTCHours(0, 0, 0, 0),
                        t
                    }
                    var i = "era"in e && 1 !== e.era ? 1 - n.year : n.year;
                    return t.setUTCFullYear(i, 0, 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Ye = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 130),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "R", "u", "Q", "q", "M", "L", "I", "d", "D", "i", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    var r = function(t) {
                        return {
                            year: t,
                            isTwoDigitYear: "YY" === e
                        }
                    };
                    switch (e) {
                    case "Y":
                        return be(Ce(4, t), r);
                    case "Yo":
                        return be(n.ordinalNumber(t, {
                            unit: "year"
                        }), r);
                    default:
                        return be(Ce(e.length, t), r)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e.isTwoDigitYear || e.year > 0
                }
            }, {
                key: "set",
                value: function(t, e, n, r) {
                    var a = q(t, r);
                    if (n.isTwoDigitYear) {
                        var i = Ae(n.year, a);
                        return t.setUTCFullYear(i, 0, r.firstWeekContainsDate),
                        t.setUTCHours(0, 0, 0, 0),
                        F(t, r)
                    }
                    var o = "era"in e && 1 !== e.era ? 1 - n.year : n.year;
                    return t.setUTCFullYear(o, 0, r.firstWeekContainsDate),
                    t.setUTCHours(0, 0, 0, 0),
                    F(t, r)
                }
            }]),
            n
        }(Zt)
          , Ne = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 130),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["G", "y", "Y", "u", "Q", "q", "M", "L", "w", "d", "D", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e) {
                    return xe("R" === e ? 4 : e.length, t)
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    var r = new Date(0);
                    return r.setUTCFullYear(n, 0, 4),
                    r.setUTCHours(0, 0, 0, 0),
                    H(r)
                }
            }]),
            n
        }(Zt)
          , Ee = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 130),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["G", "y", "Y", "R", "w", "I", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e) {
                    return xe("u" === e ? 4 : e.length, t)
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCFullYear(n, 0, 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , He = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 120),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "q", "M", "L", "w", "I", "d", "D", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "Q":
                    case "QQ":
                        return Ce(e.length, t);
                    case "Qo":
                        return n.ordinalNumber(t, {
                            unit: "quarter"
                        });
                    case "QQQ":
                        return n.quarter(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.quarter(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "QQQQQ":
                        return n.quarter(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.quarter(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.quarter(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.quarter(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 4
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMonth(3 * (n - 1), 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Oe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 120),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "Q", "M", "L", "w", "I", "d", "D", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "q":
                    case "qq":
                        return Ce(e.length, t);
                    case "qo":
                        return n.ordinalNumber(t, {
                            unit: "quarter"
                        });
                    case "qqq":
                        return n.quarter(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.quarter(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    case "qqqqq":
                        return n.quarter(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    default:
                        return n.quarter(t, {
                            width: "wide",
                            context: "standalone"
                        }) || n.quarter(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.quarter(t, {
                            width: "narrow",
                            context: "standalone"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 4
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMonth(3 * (n - 1), 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , We = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "q", "Q", "L", "w", "I", "D", "i", "e", "c", "t", "T"]),
                zt((0,
                Ot.A)(t), "priority", 110),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    var r = function(t) {
                        return t - 1
                    };
                    switch (e) {
                    case "M":
                        return be(ke(Jt, t), r);
                    case "MM":
                        return be(Ce(2, t), r);
                    case "Mo":
                        return be(n.ordinalNumber(t, {
                            unit: "month"
                        }), r);
                    case "MMM":
                        return n.month(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.month(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "MMMMM":
                        return n.month(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.month(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.month(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.month(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 11
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMonth(n, 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Le = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 110),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "q", "Q", "M", "w", "I", "D", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    var r = function(t) {
                        return t - 1
                    };
                    switch (e) {
                    case "L":
                        return be(ke(Jt, t), r);
                    case "LL":
                        return be(Ce(2, t), r);
                    case "Lo":
                        return be(n.ordinalNumber(t, {
                            unit: "month"
                        }), r);
                    case "LLL":
                        return n.month(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.month(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    case "LLLLL":
                        return n.month(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    default:
                        return n.month(t, {
                            width: "wide",
                            context: "standalone"
                        }) || n.month(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.month(t, {
                            width: "narrow",
                            context: "standalone"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 11
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMonth(n, 1),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt);
        var Fe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 100),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "i", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "w":
                        return ke(te, t);
                    case "wo":
                        return n.ordinalNumber(t, {
                            unit: "week"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 53
                }
            }, {
                key: "set",
                value: function(t, e, n, r) {
                    return F(function(t, e, n) {
                        o(2, arguments);
                        var r = u(t)
                          , i = a(e)
                          , s = I(r, n) - i;
                        return r.setUTCDate(r.getUTCDate() - 7 * s),
                        r
                    }(t, n, r), r)
                }
            }]),
            n
        }(Zt);
        var qe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 100),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "Y", "u", "q", "Q", "M", "L", "w", "d", "D", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "I":
                        return ke(te, t);
                    case "Io":
                        return n.ordinalNumber(t, {
                            unit: "week"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 53
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return H(function(t, e) {
                        o(2, arguments);
                        var n = u(t)
                          , r = a(e)
                          , i = L(n) - r;
                        return n.setUTCDate(n.getUTCDate() - 7 * i),
                        n
                    }(t, n))
                }
            }]),
            n
        }(Zt)
          , Re = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
          , Ie = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
          , je = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "subPriority", 1),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "q", "Q", "w", "I", "D", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "d":
                        return ke(Kt, t);
                    case "do":
                        return n.ordinalNumber(t, {
                            unit: "date"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    var n = Se(t.getUTCFullYear())
                      , r = t.getUTCMonth();
                    return n ? e >= 1 && e <= Ie[r] : e >= 1 && e <= Re[r]
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCDate(n),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Qe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "subpriority", 1),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["Y", "R", "q", "Q", "M", "L", "w", "I", "d", "E", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "D":
                    case "DD":
                        return ke(Vt, t);
                    case "Do":
                        return n.ordinalNumber(t, {
                            unit: "date"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return Se(t.getUTCFullYear()) ? e >= 1 && e <= 366 : e >= 1 && e <= 365
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMonth(0, n),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt);
        function Be(t, e, n) {
            var r, i, s, l, c, d, h, f;
            o(2, arguments);
            var v = S()
              , m = a(null !== (r = null !== (i = null !== (s = null !== (l = null === n || void 0 === n ? void 0 : n.weekStartsOn) && void 0 !== l ? l : null === n || void 0 === n || null === (c = n.locale) || void 0 === c || null === (d = c.options) || void 0 === d ? void 0 : d.weekStartsOn) && void 0 !== s ? s : v.weekStartsOn) && void 0 !== i ? i : null === (h = v.locale) || void 0 === h || null === (f = h.options) || void 0 === f ? void 0 : f.weekStartsOn) && void 0 !== r ? r : 0);
            if (!(m >= 0 && m <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            var g = u(t)
              , y = a(e)
              , w = ((y % 7 + 7) % 7 < m ? 7 : 0) + y - g.getUTCDay();
            return g.setUTCDate(g.getUTCDate() + w),
            g
        }
        var ze = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["D", "i", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "E":
                    case "EE":
                    case "EEE":
                        return n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "EEEEE":
                        return n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "EEEEEE":
                        return n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.day(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 6
                }
            }, {
                key: "set",
                value: function(t, e, n, r) {
                    return (t = Be(t, n, r)).setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Ge = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "E", "i", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n, r) {
                    var a = function(t) {
                        var e = 7 * Math.floor((t - 1) / 7);
                        return (t + r.weekStartsOn + 6) % 7 + e
                    };
                    switch (e) {
                    case "e":
                    case "ee":
                        return be(Ce(e.length, t), a);
                    case "eo":
                        return be(n.ordinalNumber(t, {
                            unit: "day"
                        }), a);
                    case "eee":
                        return n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "eeeee":
                        return n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "eeeeee":
                        return n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.day(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 6
                }
            }, {
                key: "set",
                value: function(t, e, n, r) {
                    return (t = Be(t, n, r)).setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Xe = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "E", "i", "e", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n, r) {
                    var a = function(t) {
                        var e = 7 * Math.floor((t - 1) / 7);
                        return (t + r.weekStartsOn + 6) % 7 + e
                    };
                    switch (e) {
                    case "c":
                    case "cc":
                        return be(Ce(e.length, t), a);
                    case "co":
                        return be(n.ordinalNumber(t, {
                            unit: "day"
                        }), a);
                    case "ccc":
                        return n.day(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "short",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    case "ccccc":
                        return n.day(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    case "cccccc":
                        return n.day(t, {
                            width: "short",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "standalone"
                        });
                    default:
                        return n.day(t, {
                            width: "wide",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "abbreviated",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "short",
                            context: "standalone"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "standalone"
                        })
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 6
                }
            }, {
                key: "set",
                value: function(t, e, n, r) {
                    return (t = Be(t, n, r)).setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt);
        var _e = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 90),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["y", "Y", "u", "q", "Q", "M", "L", "w", "d", "D", "E", "e", "c", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    var r = function(t) {
                        return 0 === t ? 7 : t
                    };
                    switch (e) {
                    case "i":
                    case "ii":
                        return Ce(e.length, t);
                    case "io":
                        return n.ordinalNumber(t, {
                            unit: "day"
                        });
                    case "iii":
                        return be(n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        }), r);
                    case "iiiii":
                        return be(n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        }), r);
                    case "iiiiii":
                        return be(n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        }), r);
                    default:
                        return be(n.day(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "short",
                            context: "formatting"
                        }) || n.day(t, {
                            width: "narrow",
                            context: "formatting"
                        }), r)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 7
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t = function(t, e) {
                        o(2, arguments);
                        var n = a(e);
                        n % 7 === 0 && (n -= 7);
                        var r = u(t)
                          , i = ((n % 7 + 7) % 7 < 1 ? 7 : 0) + n - r.getUTCDay();
                        return r.setUTCDate(r.getUTCDate() + i),
                        r
                    }(t, n),
                    t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Ze = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 80),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["b", "B", "H", "k", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "a":
                    case "aa":
                    case "aaa":
                        return n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "aaaaa":
                        return n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.dayPeriod(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCHours(Ue(n), 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , $e = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 80),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["a", "B", "H", "k", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "b":
                    case "bb":
                    case "bbb":
                        return n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "bbbbb":
                        return n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.dayPeriod(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCHours(Ue(n), 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Je = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 80),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["a", "b", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "B":
                    case "BB":
                    case "BBB":
                        return n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    case "BBBBB":
                        return n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        });
                    default:
                        return n.dayPeriod(t, {
                            width: "wide",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "abbreviated",
                            context: "formatting"
                        }) || n.dayPeriod(t, {
                            width: "narrow",
                            context: "formatting"
                        })
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCHours(Ue(n), 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Ke = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 70),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["H", "K", "k", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "h":
                        return ke(ae, t);
                    case "ho":
                        return n.ordinalNumber(t, {
                            unit: "hour"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 12
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    var r = t.getUTCHours() >= 12;
                    return r && n < 12 ? t.setUTCHours(n + 12, 0, 0, 0) : r || 12 !== n ? t.setUTCHours(n, 0, 0, 0) : t.setUTCHours(0, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , Ve = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 70),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["a", "b", "h", "K", "k", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "H":
                        return ke(ee, t);
                    case "Ho":
                        return n.ordinalNumber(t, {
                            unit: "hour"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 23
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCHours(n, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , tn = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 70),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["h", "H", "k", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "K":
                        return ke(re, t);
                    case "Ko":
                        return n.ordinalNumber(t, {
                            unit: "hour"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 11
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.getUTCHours() >= 12 && n < 12 ? t.setUTCHours(n + 12, 0, 0, 0) : t.setUTCHours(n, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , en = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 70),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["a", "b", "h", "H", "K", "t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "k":
                        return ke(ne, t);
                    case "ko":
                        return n.ordinalNumber(t, {
                            unit: "hour"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 1 && e <= 24
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    var r = n <= 24 ? n % 24 : n;
                    return t.setUTCHours(r, 0, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , nn = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 60),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "m":
                        return ke(ie, t);
                    case "mo":
                        return n.ordinalNumber(t, {
                            unit: "minute"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 59
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMinutes(n, 0, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , rn = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 50),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e, n) {
                    switch (e) {
                    case "s":
                        return ke(oe, t);
                    case "so":
                        return n.ordinalNumber(t, {
                            unit: "second"
                        });
                    default:
                        return Ce(e.length, t)
                    }
                }
            }, {
                key: "validate",
                value: function(t, e) {
                    return e >= 0 && e <= 59
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCSeconds(n, 0),
                    t
                }
            }]),
            n
        }(Zt)
          , an = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 30),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["t", "T"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e) {
                    return be(Ce(e.length, t), (function(t) {
                        return Math.floor(t * Math.pow(10, 3 - e.length))
                    }
                    ))
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return t.setUTCMilliseconds(n),
                    t
                }
            }]),
            n
        }(Zt)
          , on = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 10),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["t", "T", "x"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e) {
                    switch (e) {
                    case "X":
                        return De(ge, t);
                    case "XX":
                        return De(ye, t);
                    case "XXXX":
                        return De(we, t);
                    case "XXXXX":
                        return De(Te, t);
                    default:
                        return De(pe, t)
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return e.timestampIsSet ? t : new Date(t.getTime() - n)
                }
            }]),
            n
        }(Zt)
          , un = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 10),
                zt((0,
                Ot.A)(t), "incompatibleTokens", ["t", "T", "X"]),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t, e) {
                    switch (e) {
                    case "x":
                        return De(ge, t);
                    case "xx":
                        return De(ye, t);
                    case "xxxx":
                        return De(we, t);
                    case "xxxxx":
                        return De(Te, t);
                    default:
                        return De(pe, t)
                    }
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return e.timestampIsSet ? t : new Date(t.getTime() - n)
                }
            }]),
            n
        }(Zt)
          , sn = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 40),
                zt((0,
                Ot.A)(t), "incompatibleTokens", "*"),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t) {
                    return Me(t)
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return [new Date(1e3 * n), {
                        timestampIsSet: !0
                    }]
                }
            }]),
            n
        }(Zt)
          , ln = function(t) {
            Lt(n, t);
            var e = Rt(n);
            function n() {
                var t;
                It(this, n);
                for (var r = arguments.length, a = new Array(r), i = 0; i < r; i++)
                    a[i] = arguments[i];
                return t = e.call.apply(e, [this].concat(a)),
                zt((0,
                Ot.A)(t), "priority", 20),
                zt((0,
                Ot.A)(t), "incompatibleTokens", "*"),
                t
            }
            return Bt(n, [{
                key: "parse",
                value: function(t) {
                    return Me(t)
                }
            }, {
                key: "set",
                value: function(t, e, n) {
                    return [new Date(n), {
                        timestampIsSet: !0
                    }]
                }
            }]),
            n
        }(Zt)
          , cn = {
            G: new $t,
            y: new Pe,
            Y: new Ye,
            R: new Ne,
            u: new Ee,
            Q: new He,
            q: new Oe,
            M: new We,
            L: new Le,
            w: new Fe,
            I: new qe,
            d: new je,
            D: new Qe,
            E: new ze,
            e: new Ge,
            c: new Xe,
            i: new _e,
            a: new Ze,
            b: new $e,
            B: new Je,
            h: new Ke,
            H: new Ve,
            K: new tn,
            k: new en,
            m: new nn,
            s: new rn,
            S: new an,
            X: new on,
            x: new un,
            t: new sn,
            T: new ln
        }
          , dn = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g
          , hn = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g
          , fn = /^'([^]*?)'?$/
          , vn = /''/g
          , mn = /\S/
          , gn = /[a-zA-Z]/;
        function yn(t, e, n, r) {
            var s, l, c, d, h, f, v, m, g, y, w, p, b, k, D, M, C, x;
            o(3, arguments);
            var U = String(t)
              , A = String(e)
              , P = S()
              , Y = null !== (s = null !== (l = null === r || void 0 === r ? void 0 : r.locale) && void 0 !== l ? l : P.locale) && void 0 !== s ? s : pt;
            if (!Y.match)
                throw new RangeError("locale must contain match property");
            var N = a(null !== (c = null !== (d = null !== (h = null !== (f = null === r || void 0 === r ? void 0 : r.firstWeekContainsDate) && void 0 !== f ? f : null === r || void 0 === r || null === (v = r.locale) || void 0 === v || null === (m = v.options) || void 0 === m ? void 0 : m.firstWeekContainsDate) && void 0 !== h ? h : P.firstWeekContainsDate) && void 0 !== d ? d : null === (g = P.locale) || void 0 === g || null === (y = g.options) || void 0 === y ? void 0 : y.firstWeekContainsDate) && void 0 !== c ? c : 1);
            if (!(N >= 1 && N <= 7))
                throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
            var H = a(null !== (w = null !== (p = null !== (b = null !== (k = null === r || void 0 === r ? void 0 : r.weekStartsOn) && void 0 !== k ? k : null === r || void 0 === r || null === (D = r.locale) || void 0 === D || null === (M = D.options) || void 0 === M ? void 0 : M.weekStartsOn) && void 0 !== b ? b : P.weekStartsOn) && void 0 !== p ? p : null === (C = P.locale) || void 0 === C || null === (x = C.options) || void 0 === x ? void 0 : x.weekStartsOn) && void 0 !== w ? w : 0);
            if (!(H >= 0 && H <= 6))
                throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
            if ("" === A)
                return "" === U ? u(n) : new Date(NaN);
            var O, W = {
                firstWeekContainsDate: N,
                weekStartsOn: H,
                locale: Y
            }, L = [new _t], F = A.match(hn).map((function(t) {
                var e = t[0];
                return e in at ? (0,
                at[e])(t, Y.formatLong) : t
            }
            )).join("").match(dn), q = [], R = Et(F);
            try {
                var I = function() {
                    var e = O.value;
                    null !== r && void 0 !== r && r.useAdditionalWeekYearTokens || !st(e) || lt(e, A, t),
                    null !== r && void 0 !== r && r.useAdditionalDayOfYearTokens || !ut(e) || lt(e, A, t);
                    var n = e[0]
                      , a = cn[n];
                    if (a) {
                        var i = a.incompatibleTokens;
                        if (Array.isArray(i)) {
                            var o = q.find((function(t) {
                                return i.includes(t.token) || t.token === n
                            }
                            ));
                            if (o)
                                throw new RangeError("The format string mustn't contain `".concat(o.fullToken, "` and `").concat(e, "` at the same time"))
                        } else if ("*" === a.incompatibleTokens && q.length > 0)
                            throw new RangeError("The format string mustn't contain `".concat(e, "` and any other token at the same time"));
                        q.push({
                            token: n,
                            fullToken: e
                        });
                        var u = a.run(U, e, Y.match, W);
                        if (!u)
                            return {
                                v: new Date(NaN)
                            };
                        L.push(u.setter),
                        U = u.rest
                    } else {
                        if (n.match(gn))
                            throw new RangeError("Format string contains an unescaped latin alphabet character `" + n + "`");
                        if ("''" === e ? e = "'" : "'" === n && (e = e.match(fn)[1].replace(vn, "'")),
                        0 !== U.indexOf(e))
                            return {
                                v: new Date(NaN)
                            };
                        U = U.slice(e.length)
                    }
                };
                for (R.s(); !(O = R.n()).done; ) {
                    var j = I();
                    if ("object" === i(j))
                        return j.v
                }
            } catch (J) {
                R.e(J)
            } finally {
                R.f()
            }
            if (U.length > 0 && mn.test(U))
                return new Date(NaN);
            var Q = L.map((function(t) {
                return t.priority
            }
            )).sort((function(t, e) {
                return e - t
            }
            )).filter((function(t, e, n) {
                return n.indexOf(t) === e
            }
            )).map((function(t) {
                return L.filter((function(e) {
                    return e.priority === t
                }
                )).sort((function(t, e) {
                    return e.subPriority - t.subPriority
                }
                ))
            }
            )).map((function(t) {
                return t[0]
            }
            ))
              , B = u(n);
            if (isNaN(B.getTime()))
                return new Date(NaN);
            var z, G = E(B, T(B)), X = {}, _ = Et(Q);
            try {
                for (_.s(); !(z = _.n()).done; ) {
                    var Z = z.value;
                    if (!Z.validate(G, W))
                        return new Date(NaN);
                    var $ = Z.set(G, X, W);
                    Array.isArray($) ? (G = $[0],
                    Ht(X, $[1])) : G = $
                }
            } catch (J) {
                _.e(J)
            } finally {
                _.f()
            }
            return G
        }
        function wn(t) {
            o(1, arguments);
            var e = u(t);
            return e.setDate(1),
            e.setHours(0, 0, 0, 0),
            e
        }
        function pn(t) {
            o(1, arguments);
            var e = u(t)
              , n = new Date(0);
            return n.setFullYear(e.getFullYear(), 0, 1),
            n.setHours(0, 0, 0, 0),
            n
        }
        function Tn(t, e) {
            var n;
            o(1, arguments);
            var r = a(null !== (n = null === e || void 0 === e ? void 0 : e.additionalDigits) && void 0 !== n ? n : 2);
            if (2 !== r && 1 !== r && 0 !== r)
                throw new RangeError("additionalDigits must be 0, 1 or 2");
            if ("string" !== typeof t && "[object String]" !== Object.prototype.toString.call(t))
                return new Date(NaN);
            var i, u = function(t) {
                var e, n = {}, r = t.split(bn.dateTimeDelimiter);
                if (r.length > 2)
                    return n;
                /:/.test(r[0]) ? e = r[0] : (n.date = r[0],
                e = r[1],
                bn.timeZoneDelimiter.test(n.date) && (n.date = t.split(bn.timeZoneDelimiter)[0],
                e = t.substr(n.date.length, t.length)));
                if (e) {
                    var a = bn.timezone.exec(e);
                    a ? (n.time = e.replace(a[1], ""),
                    n.timezone = a[1]) : n.time = e
                }
                return n
            }(t);
            if (u.date) {
                var s = function(t, e) {
                    var n = new RegExp("^(?:(\\d{4}|[+-]\\d{" + (4 + e) + "})|(\\d{2}|[+-]\\d{" + (2 + e) + "})$)")
                      , r = t.match(n);
                    if (!r)
                        return {
                            year: NaN,
                            restDateString: ""
                        };
                    var a = r[1] ? parseInt(r[1]) : null
                      , i = r[2] ? parseInt(r[2]) : null;
                    return {
                        year: null === i ? a : 100 * i,
                        restDateString: t.slice((r[1] || r[2]).length)
                    }
                }(u.date, r);
                i = function(t, e) {
                    if (null === e)
                        return new Date(NaN);
                    var n = t.match(kn);
                    if (!n)
                        return new Date(NaN);
                    var r = !!n[4]
                      , a = Cn(n[1])
                      , i = Cn(n[2]) - 1
                      , o = Cn(n[3])
                      , u = Cn(n[4])
                      , s = Cn(n[5]) - 1;
                    if (r)
                        return function(t, e, n) {
                            return e >= 1 && e <= 53 && n >= 0 && n <= 6
                        }(0, u, s) ? function(t, e, n) {
                            var r = new Date(0);
                            r.setUTCFullYear(t, 0, 4);
                            var a = r.getUTCDay() || 7
                              , i = 7 * (e - 1) + n + 1 - a;
                            return r.setUTCDate(r.getUTCDate() + i),
                            r
                        }(e, u, s) : new Date(NaN);
                    var l = new Date(0);
                    return function(t, e, n) {
                        return e >= 0 && e <= 11 && n >= 1 && n <= (Un[e] || (An(t) ? 29 : 28))
                    }(e, i, o) && function(t, e) {
                        return e >= 1 && e <= (An(t) ? 366 : 365)
                    }(e, a) ? (l.setUTCFullYear(e, i, Math.max(a, o)),
                    l) : new Date(NaN)
                }(s.restDateString, s.year)
            }
            if (!i || isNaN(i.getTime()))
                return new Date(NaN);
            var l, c = i.getTime(), d = 0;
            if (u.time && (d = function(t) {
                var e = t.match(Dn);
                if (!e)
                    return NaN;
                var n = xn(e[1])
                  , r = xn(e[2])
                  , a = xn(e[3]);
                if (!function(t, e, n) {
                    if (24 === t)
                        return 0 === e && 0 === n;
                    return n >= 0 && n < 60 && e >= 0 && e < 60 && t >= 0 && t < 25
                }(n, r, a))
                    return NaN;
                return n * x + r * C + 1e3 * a
            }(u.time),
            isNaN(d)))
                return new Date(NaN);
            if (!u.timezone) {
                var h = new Date(c + d)
                  , f = new Date(0);
                return f.setFullYear(h.getUTCFullYear(), h.getUTCMonth(), h.getUTCDate()),
                f.setHours(h.getUTCHours(), h.getUTCMinutes(), h.getUTCSeconds(), h.getUTCMilliseconds()),
                f
            }
            return l = function(t) {
                if ("Z" === t)
                    return 0;
                var e = t.match(Mn);
                if (!e)
                    return 0;
                var n = "+" === e[1] ? -1 : 1
                  , r = parseInt(e[2])
                  , a = e[3] && parseInt(e[3]) || 0;
                if (!function(t, e) {
                    return e >= 0 && e <= 59
                }(0, a))
                    return NaN;
                return n * (r * x + a * C)
            }(u.timezone),
            isNaN(l) ? new Date(NaN) : new Date(c + d + l)
        }
        var bn = {
            dateTimeDelimiter: /[T ]/,
            timeZoneDelimiter: /[Z ]/i,
            timezone: /([Z+-].*)$/
        }
          , kn = /^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/
          , Dn = /^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/
          , Mn = /^([+-])(\d{2})(?::?(\d{2}))?$/;
        function Cn(t) {
            return t ? parseInt(t) : 1
        }
        function xn(t) {
            return t && parseFloat(t.replace(",", ".")) || 0
        }
        var Un = [31, null, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        function An(t) {
            return t % 400 === 0 || t % 4 === 0 && t % 100 !== 0
        }
        var Sn = n(93398)
          , Pn = n.n(Sn);
        const Yn = {
            y: {
                sectionType: "year",
                contentType: "digit",
                maxLength: 4
            },
            yy: "year",
            yyy: {
                sectionType: "year",
                contentType: "digit",
                maxLength: 4
            },
            yyyy: "year",
            M: {
                sectionType: "month",
                contentType: "digit",
                maxLength: 2
            },
            MM: "month",
            MMMM: {
                sectionType: "month",
                contentType: "letter"
            },
            MMM: {
                sectionType: "month",
                contentType: "letter"
            },
            L: {
                sectionType: "month",
                contentType: "digit",
                maxLength: 2
            },
            LL: "month",
            LLL: {
                sectionType: "month",
                contentType: "letter"
            },
            LLLL: {
                sectionType: "month",
                contentType: "letter"
            },
            d: {
                sectionType: "day",
                contentType: "digit",
                maxLength: 2
            },
            dd: "day",
            do: {
                sectionType: "day",
                contentType: "digit-with-letter"
            },
            E: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            EE: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            EEE: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            EEEE: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            EEEEE: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            i: {
                sectionType: "weekDay",
                contentType: "digit",
                maxLength: 1
            },
            ii: "weekDay",
            iii: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            iiii: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            e: {
                sectionType: "weekDay",
                contentType: "digit",
                maxLength: 1
            },
            ee: "weekDay",
            eee: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            eeee: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            eeeee: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            eeeeee: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            c: {
                sectionType: "weekDay",
                contentType: "digit",
                maxLength: 1
            },
            cc: "weekDay",
            ccc: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            cccc: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            ccccc: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            cccccc: {
                sectionType: "weekDay",
                contentType: "letter"
            },
            a: "meridiem",
            aa: "meridiem",
            aaa: "meridiem",
            H: {
                sectionType: "hours",
                contentType: "digit",
                maxLength: 2
            },
            HH: "hours",
            h: {
                sectionType: "hours",
                contentType: "digit",
                maxLength: 2
            },
            hh: "hours",
            m: {
                sectionType: "minutes",
                contentType: "digit",
                maxLength: 2
            },
            mm: "minutes",
            s: {
                sectionType: "seconds",
                contentType: "digit",
                maxLength: 2
            },
            ss: "seconds"
        }
          , Nn = {
            year: "yyyy",
            month: "LLLL",
            monthShort: "MMM",
            dayOfMonth: "d",
            weekday: "EEEE",
            weekdayShort: "EEEEEE",
            hours24h: "HH",
            hours12h: "hh",
            meridiem: "aa",
            minutes: "mm",
            seconds: "ss",
            fullDate: "PP",
            fullDateWithWeekday: "PPPP",
            keyboardDate: "P",
            shortDate: "MMM d",
            normalDate: "d MMMM",
            normalDateWithWeekday: "EEE, MMM d",
            monthAndYear: "LLLL yyyy",
            monthAndDate: "MMMM d",
            fullTime: "p",
            fullTime12h: "hh:mm aa",
            fullTime24h: "HH:mm",
            fullDateTime: "PP p",
            fullDateTime12h: "PP hh:mm aa",
            fullDateTime24h: "PP HH:mm",
            keyboardDateTime: "P p",
            keyboardDateTime12h: "P hh:mm aa",
            keyboardDateTime24h: "P HH:mm"
        };
        class En {
            constructor({locale: t, formats: e}={}) {
                this.isMUIAdapter = !0,
                this.isTimezoneCompatible = !1,
                this.lib = "date-fns",
                this.locale = void 0,
                this.formats = void 0,
                this.formatTokenMap = Yn,
                this.escapedCharacters = {
                    start: "'",
                    end: "'"
                },
                this.date = t => "undefined" === typeof t ? new Date : null === t ? null : new Date(t),
                this.dateWithTimezone = t => this.date(t),
                this.getTimezone = () => "default",
                this.setTimezone = t => t,
                this.toJsDate = t => t,
                this.parseISO = t => Tn(t),
                this.toISO = t => function(t, e) {
                    var n, r;
                    o(1, arguments);
                    var a = u(t);
                    if (isNaN(a.getTime()))
                        throw new RangeError("Invalid time value");
                    var i = String(null !== (n = null === e || void 0 === e ? void 0 : e.format) && void 0 !== n ? n : "extended")
                      , s = String(null !== (r = null === e || void 0 === e ? void 0 : e.representation) && void 0 !== r ? r : "complete");
                    if ("extended" !== i && "basic" !== i)
                        throw new RangeError("format must be 'extended' or 'basic'");
                    if ("date" !== s && "time" !== s && "complete" !== s)
                        throw new RangeError("representation must be 'date', 'time', or 'complete'");
                    var l = ""
                      , c = ""
                      , d = "extended" === i ? "-" : ""
                      , h = "extended" === i ? ":" : "";
                    if ("time" !== s) {
                        var f = j(a.getDate(), 2)
                          , v = j(a.getMonth() + 1, 2)
                          , m = j(a.getFullYear(), 4);
                        l = "".concat(m).concat(d).concat(v).concat(d).concat(f)
                    }
                    if ("date" !== s) {
                        var g = a.getTimezoneOffset();
                        if (0 !== g) {
                            var y = Math.abs(g)
                              , w = j(Math.floor(y / 60), 2)
                              , p = j(y % 60, 2);
                            c = "".concat(g < 0 ? "+" : "-").concat(w, ":").concat(p)
                        } else
                            c = "Z";
                        var T = "" === l ? "" : "T"
                          , b = [j(a.getHours(), 2), j(a.getMinutes(), 2), j(a.getSeconds(), 2)].join(h);
                        l = "".concat(l).concat(T).concat(b).concat(c)
                    }
                    return l
                }(t, {
                    format: "extended"
                }),
                this.parse = (t, e) => "" === t ? null : yn(t, e, new Date, {
                    locale: this.locale
                }),
                this.getCurrentLocaleCode = () => {
                    var t;
                    return (null == (t = this.locale) ? void 0 : t.code) || "en-US"
                }
                ,
                this.is12HourCycleInCurrentLocale = () => !this.locale || /a/.test(this.locale.formatLong.time()),
                this.expandFormat = t => t.match(/P+p+|P+|p+|''|'(''|[^'])+('|$)|./g).map((t => {
                    const e = t[0];
                    if ("p" === e || "P" === e) {
                        return (0,
                        Pn()[e])(t, (this.locale || wt).formatLong, {})
                    }
                    return t
                }
                )).join(""),
                this.getFormatHelperText = t => this.expandFormat(t).replace(/(aaa|aa|a)/g, "(a|p)m").toLocaleLowerCase(),
                this.isNull = t => null === t,
                this.isValid = t => N(this.date(t)),
                this.format = (t, e) => this.formatByString(t, this.formats[e]),
                this.formatByString = (t, e) => Ct(t, e, {
                    locale: this.locale
                }),
                this.formatNumber = t => t,
                this.getDiff = (t, e, n) => {
                    switch (n) {
                    case "years":
                        return f(t, this.date(e));
                    case "quarters":
                        return function(t, e, n) {
                            o(2, arguments);
                            var r = g(t, e) / 3;
                            return p(null === n || void 0 === n ? void 0 : n.roundingMethod)(r)
                        }(t, this.date(e));
                    case "months":
                        return g(t, this.date(e));
                    case "weeks":
                        return function(t, e, n) {
                            o(2, arguments);
                            var r = M(t, e) / 7;
                            return p(null === n || void 0 === n ? void 0 : n.roundingMethod)(r)
                        }(t, this.date(e));
                    case "days":
                        return M(t, this.date(e));
                    case "hours":
                        return function(t, e, n) {
                            o(2, arguments);
                            var r = U(t, e) / x;
                            return p(null === n || void 0 === n ? void 0 : n.roundingMethod)(r)
                        }(t, this.date(e));
                    case "minutes":
                        return function(t, e, n) {
                            o(2, arguments);
                            var r = U(t, e) / C;
                            return p(null === n || void 0 === n ? void 0 : n.roundingMethod)(r)
                        }(t, this.date(e));
                    case "seconds":
                        return function(t, e, n) {
                            o(2, arguments);
                            var r = U(t, e) / 1e3;
                            return p(null === n || void 0 === n ? void 0 : n.roundingMethod)(r)
                        }(t, this.date(e));
                    default:
                        return U(t, this.date(e))
                    }
                }
                ,
                this.isEqual = (t, e) => null === t && null === e || function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = u(e);
                    return n.getTime() === r.getTime()
                }(t, e),
                this.isSameYear = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = u(e);
                    return n.getFullYear() === r.getFullYear()
                }(t, e),
                this.isSameMonth = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = u(e);
                    return n.getFullYear() === r.getFullYear() && n.getMonth() === r.getMonth()
                }(t, e),
                this.isSameDay = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = b(t)
                      , r = b(e);
                    return n.getTime() === r.getTime()
                }(t, e),
                this.isSameHour = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = Yt(t)
                      , r = Yt(e);
                    return n.getTime() === r.getTime()
                }(t, e),
                this.isAfter = (t, e) => St(t, e),
                this.isAfterYear = (t, e) => St(t, Y(e)),
                this.isAfterDay = (t, e) => St(t, v(e)),
                this.isBefore = (t, e) => Pt(t, e),
                this.isBeforeYear = (t, e) => Pt(t, pn(e)),
                this.isBeforeDay = (t, e) => Pt(t, b(e)),
                this.isWithinRange = (t, [e,n]) => function(t, e) {
                    o(2, arguments);
                    var n = u(t).getTime()
                      , r = u(e.start).getTime()
                      , a = u(e.end).getTime();
                    if (!(r <= a))
                        throw new RangeError("Invalid interval");
                    return n >= r && n <= a
                }(t, {
                    start: e,
                    end: n
                }),
                this.startOfYear = t => pn(t),
                this.startOfMonth = t => wn(t),
                this.startOfWeek = t => Ut(t, {
                    locale: this.locale
                }),
                this.startOfDay = t => b(t),
                this.endOfYear = t => Y(t),
                this.endOfMonth = t => m(t),
                this.endOfWeek = t => P(t, {
                    locale: this.locale
                }),
                this.endOfDay = t => v(t),
                this.addYears = (t, e) => d(t, e),
                this.addMonths = (t, e) => c(t, e),
                this.addWeeks = (t, e) => function(t, e) {
                    return o(2, arguments),
                    s(t, 7 * a(e))
                }(t, e),
                this.addDays = (t, e) => s(t, e),
                this.addHours = (t, e) => function(t, e) {
                    return o(2, arguments),
                    l(t, 36e5 * a(e))
                }(t, e),
                this.addMinutes = (t, e) => function(t, e) {
                    return o(2, arguments),
                    l(t, 6e4 * a(e))
                }(t, e),
                this.addSeconds = (t, e) => function(t, e) {
                    return o(2, arguments),
                    l(t, 1e3 * a(e))
                }(t, e),
                this.getYear = t => function(t) {
                    return o(1, arguments),
                    u(t).getFullYear()
                }(t),
                this.getMonth = t => function(t) {
                    return o(1, arguments),
                    u(t).getMonth()
                }(t),
                this.getDate = t => function(t) {
                    return o(1, arguments),
                    u(t).getDate()
                }(t),
                this.getHours = t => function(t) {
                    return o(1, arguments),
                    u(t).getHours()
                }(t),
                this.getMinutes = t => function(t) {
                    return o(1, arguments),
                    u(t).getMinutes()
                }(t),
                this.getSeconds = t => function(t) {
                    return o(1, arguments),
                    u(t).getSeconds()
                }(t),
                this.getMilliseconds = t => function(t) {
                    return o(1, arguments),
                    u(t).getMilliseconds()
                }(t),
                this.setYear = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return isNaN(n.getTime()) ? new Date(NaN) : (n.setFullYear(r),
                    n)
                }(t, e),
                this.setMonth = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e)
                      , i = n.getFullYear()
                      , s = n.getDate()
                      , l = new Date(0);
                    l.setFullYear(i, r, 15),
                    l.setHours(0, 0, 0, 0);
                    var c = xt(l);
                    return n.setMonth(r, Math.min(s, c)),
                    n
                }(t, e),
                this.setDate = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return n.setDate(r),
                    n
                }(t, e),
                this.setHours = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return n.setHours(r),
                    n
                }(t, e),
                this.setMinutes = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return n.setMinutes(r),
                    n
                }(t, e),
                this.setSeconds = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return n.setSeconds(r),
                    n
                }(t, e),
                this.setMilliseconds = (t, e) => function(t, e) {
                    o(2, arguments);
                    var n = u(t)
                      , r = a(e);
                    return n.setMilliseconds(r),
                    n
                }(t, e),
                this.getDaysInMonth = t => xt(t),
                this.getNextMonth = t => c(t, 1),
                this.getPreviousMonth = t => c(t, -1),
                this.getMonthArray = t => {
                    const e = [pn(t)];
                    for (; e.length < 12; ) {
                        const t = e[e.length - 1];
                        e.push(this.getNextMonth(t))
                    }
                    return e
                }
                ,
                this.mergeDateAndTime = (t, e) => this.setSeconds(this.setMinutes(this.setHours(t, this.getHours(e)), this.getMinutes(e)), this.getSeconds(e)),
                this.getWeekdays = () => {
                    const t = new Date;
                    return function(t, e) {
                        var n;
                        o(1, arguments);
                        var r = t || {}
                          , a = u(r.start)
                          , i = u(r.end).getTime();
                        if (!(a.getTime() <= i))
                            throw new RangeError("Invalid interval");
                        var s = []
                          , l = a;
                        l.setHours(0, 0, 0, 0);
                        var c = Number(null !== (n = null === e || void 0 === e ? void 0 : e.step) && void 0 !== n ? n : 1);
                        if (c < 1 || isNaN(c))
                            throw new RangeError("`options.step` must be a number greater than 1");
                        for (; l.getTime() <= i; )
                            s.push(u(l)),
                            l.setDate(l.getDate() + c),
                            l.setHours(0, 0, 0, 0);
                        return s
                    }({
                        start: Ut(t, {
                            locale: this.locale
                        }),
                        end: P(t, {
                            locale: this.locale
                        })
                    }).map((t => this.formatByString(t, "EEEEEE")))
                }
                ,
                this.getWeekArray = t => {
                    const e = Ut(wn(t), {
                        locale: this.locale
                    })
                      , n = P(m(t), {
                        locale: this.locale
                    });
                    let r = 0
                      , a = e;
                    const i = [];
                    for (; Pt(a, n); ) {
                        const t = Math.floor(r / 7);
                        i[t] = i[t] || [],
                        i[t].push(a),
                        a = s(a, 1),
                        r += 1
                    }
                    return i
                }
                ,
                this.getWeekNumber = t => function(t, e) {
                    o(1, arguments);
                    var n = u(t)
                      , r = Ut(n, e).getTime() - At(n, e).getTime();
                    return Math.round(r / 6048e5) + 1
                }(t, {
                    locale: this.locale
                }),
                this.getYearRange = (t, e) => {
                    const n = pn(t)
                      , r = Y(e)
                      , a = [];
                    let i = n;
                    for (; Pt(i, r); )
                        a.push(i),
                        i = d(i, 1);
                    return a
                }
                ,
                this.getMeridiemText = t => "am" === t ? "AM" : "PM",
                this.locale = t,
                this.formats = (0,
                r.A)({}, Nn, e)
            }
        }
    }
    ,
    93398: (t, e) => {
        Object.defineProperty(e, "__esModule", {
            value: !0
        }),
        e.default = void 0;
        var n = function(t, e) {
            switch (t) {
            case "P":
                return e.date({
                    width: "short"
                });
            case "PP":
                return e.date({
                    width: "medium"
                });
            case "PPP":
                return e.date({
                    width: "long"
                });
            default:
                return e.date({
                    width: "full"
                })
            }
        }
          , r = function(t, e) {
            switch (t) {
            case "p":
                return e.time({
                    width: "short"
                });
            case "pp":
                return e.time({
                    width: "medium"
                });
            case "ppp":
                return e.time({
                    width: "long"
                });
            default:
                return e.time({
                    width: "full"
                })
            }
        }
          , a = {
            p: r,
            P: function(t, e) {
                var a, i = t.match(/(P+)(p+)?/) || [], o = i[1], u = i[2];
                if (!u)
                    return n(t, e);
                switch (o) {
                case "P":
                    a = e.dateTime({
                        width: "short"
                    });
                    break;
                case "PP":
                    a = e.dateTime({
                        width: "medium"
                    });
                    break;
                case "PPP":
                    a = e.dateTime({
                        width: "long"
                    });
                    break;
                default:
                    a = e.dateTime({
                        width: "full"
                    })
                }
                return a.replace("{{date}}", n(o, e)).replace("{{time}}", r(u, e))
            }
        };
        e.default = a,
        t.exports = e.default
    }
}]);
