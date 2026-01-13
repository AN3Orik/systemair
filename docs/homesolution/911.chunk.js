"use strict";
(self.webpackChunk_systemair_portal = self.webpackChunk_systemair_portal || []).push([[911], {
    43911: (e, t, i) => {
        i.r(t),
        i.d(t, {
            default: () => Ie
        });
        var n = i(36870)
          , a = i(64180)
          , s = i(25706)
          , o = i(96645)
          , r = i(86326)
          , l = i(42027)
          , d = i(49134)
          , c = i(77608)
          , p = i(44803)
          , u = i(67382);
        const x = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    transition: all 200ms ease;
    display: flex;
    align-items: center;
    ${e => e.hasRoute ? "\n    cursor: pointer;\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    " : "\n    "}
`
          , h = u.Ay.div`
    display: flex;
    flex-direction: column;
    font: 400 12px Roboto;
    align-items: left;
`
          , m = ({properties: e}) => {
            const t = (0,
            l.Zp)()
              , {translate: i} = (0,
            d.B)()
              , a = () => {
                e.route && t(e.route)
            }
            ;
            return (0,
            r.useMemo)(( () => (0,
            n.jsxs)(x, Object.assign({
                onClick: a,
                hasRoute: !!e.route,
                "data-testid": e.key
            }, {
                children: [e.icon && (0,
                n.jsx)("div", Object.assign({
                    style: {
                        width: "32px",
                        display: "flex"
                    }
                }, {
                    children: (0,
                    n.jsx)(c.g, {
                        icon: e.icon,
                        color: "#004985",
                        style: {
                            fontSize: "20px"
                        }
                    })
                })), (0,
                n.jsxs)(h, Object.assign({
                    style: {
                        cursor: e.route ? "pointer" : "default"
                    }
                }, {
                    children: [(0,
                    n.jsx)(p.o5, {
                        text: i(e.title),
                        testId: e.route,
                        size: "SMALL_PLUS",
                        type: "PRIMARY",
                        face: "ROBOTO",
                        style: {
                            padding: "4px 0",
                            cursor: e.route ? "pointer" : "default"
                        }
                    }), (0,
                    n.jsx)(p.o5, {
                        text: e.description ? i(e.description) : "",
                        size: "SMALL",
                        type: "DISABLED",
                        face: "ROBOTO",
                        style: {
                            cursor: e.route ? "pointer" : "default"
                        }
                    })]
                }))]
            }))), [e])
        }
        ;
        var g = i(93967);
        const y = u.Ay.div`
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: auto;
    min-height: 72px;
    padding: 2px 16px;
    border-bottom: 2px solid #86a3a9;
    transition: all 200ms ease;
    ${e => e.hasRoute ? "\n    cursor: pointer;\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    " : "\n    "}
`
          , v = u.Ay.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
`
          , f = u.Ay.div`
    margin: 0 0 4px 0;
    @media only screen and (min-width: 0px) and (max-width: ${ ({theme: e}) => e.breakpoints.SMALL}px) {
        margin-bottom: ${e => e.wrappedText > 80 ? "8px" : "4px"};
    }
`
          , j = (u.Ay.div`
    background-color: #00ff00;
    margin: 0 0 4px 0;
    @media only screen and (min-width: 0px) and (max-width: ${ ({theme: e}) => e.breakpoints.SMALL}px) {
        margin-bottom: ${e => e.wrappedText > 30 ? "8px" : "4px"};
        background-color: #ffff00;
    }
`,
        ({direction: e, onClose: t, props: i, active: a}) => {
            const {translate: s} = (0,
            d.B)();
            return (0,
            n.jsx)(p.rk, Object.assign({
                active: a,
                onClose: () => t(),
                direction: e,
                title: i.title,
                testId: i.testId
            }, {
                children: i.dataItem.options.map((e => (0,
                n.jsx)(p.$n, {
                    text: s(e.title, e.translationVariables),
                    variant: i.dataItem.value === e.value ? "PRIMARY" : "DISCREET",
                    onClick: () => {
                        t(e)
                    }
                    ,
                    testId: `option-${e.value}`
                }, `${e.value}`)))
            }))
        }
        )
          , b = ({properties: e, onWriteDataItem: t}) => {
            const i = (0,
            l.Zp)()
              , {translateDataItemUnit: u} = (0,
            o.j$)()
              , {popStack: x, pushStack: h} = (0,
            s.hS)()
              , {translate: m} = (0,
            d.B)()
              , b = {};
            (0,
            r.useEffect)(( () => {
                const e = document.querySelectorAll(".textWrap");
                for (const t of e)
                    b[t.id] = document.getElementById(t.id).clientHeight > 28
            }
            ), []);
            const O = e => {
                var t;
                if ("string" === typeof e)
                    return m(e);
                const i = e.dataItem;
                let n = "unknown";
                if (i.type === g.CP.NUMBER) {
                    const e = i
                      , t = void 0 !== e.unit ? u(e.unit) : "";
                    n = `${e.decimals ? (e.value / Math.pow(10, e.decimals)).toFixed(e.decimals) : e.value} ${t}`
                } else if (i.type === g.CP.ENUM) {
                    const e = i;
                    n = m((null === (t = e.options.find((t => t.value === e.value))) || void 0 === t ? void 0 : t.title) || "unknown enum")
                } else if (i.type === g.CP.BOOLEAN) {
                    n = !0 === i.value ? "ON" : "OFF"
                } else if (i.type === g.CP.STRING) {
                    n = i.value
                }
                return n
            }
              , A = []
              , w = (0,
            r.useMemo)(( () => e.rows.map(( (t, i) => {
                if (A.some((e => e === i)))
                    return;
                let a = "";
                return a = t.join ? [t, ...e.rows.filter(( (e, n) => {
                    var a, s;
                    if ((null === (a = e.join) || void 0 === a ? void 0 : a.id) === (null === (s = t.join) || void 0 === s ? void 0 : s.id) && n !== i)
                        return A.push(n),
                        !0
                }
                ))].map((e => O(e.value).trim())).join(t.join.joiner).trim() : O(t.value),
                (0,
                n.jsx)("div", Object.assign({
                    "data-testid": `row-${i}`
                }, {
                    children: (0,
                    n.jsx)(f, Object.assign({
                        className: "textWrap",
                        id: `textWrap-${i}`,
                        wrappedText: m(t.title).length + a.length
                    }, {
                        children: (0,
                        n.jsxs)("div", Object.assign({
                            style: {
                                display: "flex",
                                flexFlow: "wrap"
                            }
                        }, {
                            children: [(0,
                            n.jsx)(p.o5, {
                                text: `${m(t.title)}${t.title ? ":" : ""}`,
                                testId: "key",
                                size: "SMALL",
                                face: "ROBOTO",
                                type: "DISABLED",
                                style: {
                                    cursor: e.route ? "pointer" : "default"
                                }
                            }), (0,
                            n.jsx)(p.o5, {
                                text: a,
                                testId: "value",
                                size: t.highlighted ? "SMALL_PLUS" : "SMALL",
                                face: "ROBOTO",
                                type: t.highlighted ? "PRIMARY" : "DISABLED",
                                style: {
                                    marginLeft: "2px",
                                    cursor: e.route ? "pointer" : "default"
                                }
                            }, t.title + t.value)]
                        }))
                    }), i)
                }), i)
            }
            ))), [e]);
            return (0,
            n.jsx)(y, Object.assign({
                hasRoute: !!e.route,
                onClick: () => {
                    if (e.itemDialog) {
                        const i = e.itemDialog;
                        if (i.dataItem.type === g.CP.ENUM) {
                            const n = i.dataItem;
                            return void h({
                                component: j,
                                props: {
                                    dataItem: n,
                                    title: m(e.title, e.translationVariables)
                                },
                                onClose: e => {
                                    e && t(Object.assign(Object.assign({}, n), {
                                        value: e.value
                                    })),
                                    x()
                                }
                            })
                        }
                    }
                    e.route && i(e.route)
                }
                ,
                "data-testid": e.key
            }, {
                children: (0,
                n.jsxs)(v, {
                    children: [(0,
                    n.jsxs)("div", {
                        children: [(0,
                        n.jsx)(p.o5, {
                            text: m(e.title, e.translationVariables),
                            testId: "title",
                            size: "SMALL_PLUS",
                            type: "PRIMARY",
                            face: "ROBOTO",
                            style: {
                                padding: "4px 0",
                                cursor: "pointer"
                            }
                        }), w]
                    }), !e.route && (0,
                    n.jsx)(c.g, {
                        color: "#86a3a9",
                        "data-testid": "lock-icon",
                        icon: a.DW4
                    })]
                })
            }))
        }
          , O = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;

    ${ ({inactive: e, readOnly: t, theme: i}) => e || t ? "" : `\n    cursor: pointer;\n    @media only screen and (min-width: 0px) and (max-width: ${i.breakpoints.MEDIUM}px) {\n        cursor: default;\n    }\n\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    `}
`
          , A = u.Ay.div`
    white-space: normal;
    font: 400 14px Roboto;
    width: 100%;
`
          , w = (u.Ay.div`
    min-height: 36px;
    height: auto;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;
    color: #000;
    width: 100%;
    font: 400 14px Roboto;
    padding: 16px;

    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
`,
        u.Ay.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
`)
          , I = ({onWriteDataItem: e, properties: t, readOnly: i, title: r, testId: l, description: u}) => {
            const {translate: x} = (0,
            d.B)()
              , {popStack: h, pushStack: m} = (0,
            s.hS)();
            return (0,
            n.jsx)(O, Object.assign({
                inactive: !1,
                readOnly: i,
                "data-testid": l,
                onClick: () => {
                    i || m({
                        component: o.fb,
                        props: {
                            dataItem: t,
                            title: x(r),
                            testId: l
                        },
                        onClose: i => {
                            i && e(Object.assign(Object.assign({}, t), {
                                value: i.value
                            })),
                            h()
                        }
                    })
                }
            }, {
                children: (0,
                n.jsx)(A, {
                    children: (0,
                    n.jsxs)(w, {
                        children: [(0,
                        n.jsxs)("div", {
                            children: [(0,
                            n.jsx)(p.o5, {
                                text: x(r),
                                type: "PRIMARY",
                                size: "SMALL_PLUS",
                                face: "ROBOTO"
                            }), u && (0,
                            n.jsx)(p.o5, {
                                text: x(u),
                                size: "SMALL",
                                type: "DISABLED",
                                face: "ROBOTO",
                                style: {
                                    margin: "4px 0 6px 0"
                                }
                            }), (0,
                            n.jsx)(p.o5, {
                                text: ( () => {
                                    var e;
                                    return x((null === (e = t.options.find((e => e.value === t.value))) || void 0 === e ? void 0 : e.title) || "unknown")
                                }
                                )(),
                                size: "SMALL_PLUS",
                                face: "ROBOTO",
                                style: {
                                    marginTop: "2px"
                                }
                            })]
                        }), i && (0,
                        n.jsx)(c.g, {
                            color: "#86a3a9",
                            "data-testid": "lock-icon",
                            icon: a.DW4
                        })]
                    })
                })
            }))
        }
          , S = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;

    ${ ({theme: e, inactive: t, readOnly: i}) => t || i ? "\n    " : `\n    cursor: pointer;\n    @media only screen and (min-width: 0px) and (max-width: ${e.breakpoints.MEDIUM}px) {\n        cursor: default;\n    }\n\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    `}
`
          , k = u.Ay.div`
    white-space: normal;
    font: 400 14px Roboto;
    width: 100%;
`
          , D = u.Ay.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
`
          , E = (u.Ay.div`
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
`,
        ({onWriteDataItem: e, properties: t, readOnly: i, title: r, description: l, testId: u}) => {
            const {translateDataItemUnit: x} = (0,
            o.j$)()
              , {translate: h} = (0,
            d.B)()
              , {popStack: m, pushStack: g} = (0,
            s.hS)();
            return (0,
            n.jsx)(S, Object.assign({
                inactive: !1,
                readOnly: i,
                "data-testid": u,
                onClick: () => {
                    i || g({
                        component: o.BG,
                        props: {
                            dataItem: t,
                            title: h(r),
                            testId: u,
                            description: l ? h(l) : ""
                        },
                        onClose: i => {
                            void 0 !== i && e(Object.assign(Object.assign({}, t), {
                                value: i
                            })),
                            m()
                        }
                    })
                }
            }, {
                children: (0,
                n.jsx)(k, {
                    children: (0,
                    n.jsxs)(D, {
                        children: [(0,
                        n.jsxs)("div", {
                            children: [(0,
                            n.jsx)(p.o5, {
                                text: h(r),
                                size: "SMALL_PLUS",
                                face: "ROBOTO",
                                type: "PRIMARY"
                            }), l && (0,
                            n.jsx)(p.o5, {
                                text: h(l),
                                size: "SMALL",
                                face: "ROBOTO",
                                style: {
                                    margin: "4px 0 6px 0"
                                }
                            }), (0,
                            n.jsx)(p.o5, {
                                text: `${t.decimals ? (t.value / Math.pow(10, t.decimals)).toFixed(t.decimals) : t.value} ${void 0 !== t.unit ? x(t.unit) : ""}`,
                                size: "SMALL_PLUS",
                                face: "ROBOTO",
                                style: {
                                    marginTop: "2px"
                                },
                                testId: "value"
                            })]
                        }), i && (0,
                        n.jsx)(c.g, {
                            color: "#86a3a9",
                            "data-testid": "lock-icon",
                            icon: a.DW4
                        })]
                    })
                })
            }))
        }
        )
          , L = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;

    ${ ({inactive: e, readOnly: t, theme: i}) => e || t ? "\n    " : `\n    cursor: pointer;\n    @media only screen and (min-width: 0px) and (max-width: ${i.breakpoints.MEDIUM}px) {\n        cursor: default;\n    }\n\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    `}
`
          , R = u.Ay.div`
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
`
          , M = u.Ay.div`
    padding: 0;
`
          , T = u.Ay.div`
    display: flex;
    font: 400 12px Roboto;
`
          , C = (u.Ay.img`
    height: 64px;
    width: 64px;
`,
        ({onWriteDataItem: e, properties: t, readOnly: i, title: s, description: o, testId: r}) => {
            const {translate: l} = (0,
            d.B)();
            return (0,
            n.jsx)(L, Object.assign({
                inactive: !1,
                readOnly: i,
                "data-testid": r
            }, {
                children: (0,
                n.jsxs)(R, {
                    children: [(0,
                    n.jsx)(M, {
                        children: (0,
                        n.jsx)(T, {
                            children: (0,
                            n.jsxs)("div", {
                                children: [(0,
                                n.jsx)(p.o5, {
                                    size: "SMALL_PLUS",
                                    text: l(s),
                                    face: "ROBOTO",
                                    type: "PRIMARY"
                                }), o && (0,
                                n.jsx)(p.o5, {
                                    size: "SMALL",
                                    text: l(o),
                                    face: "ROBOTO",
                                    type: "DISABLED",
                                    style: {
                                        margin: "4px 0 6px 0"
                                    }
                                })]
                            })
                        })
                    }), (0,
                    n.jsxs)("div", Object.assign({
                        style: {
                            display: "flex",
                            alignItems: "center"
                        }
                    }, {
                        children: [(0,
                        n.jsx)(p.dO, {
                            checked: t.value,
                            onChange: i => {
                                e(Object.assign(Object.assign({}, t), {
                                    value: i
                                }))
                            }
                            ,
                            testId: "enable"
                        }), i && (0,
                        n.jsx)(c.g, {
                            color: "#86a3a9",
                            icon: a.DW4,
                            style: {
                                marginLeft: "8px"
                            },
                            "data-testid": "lock-icon"
                        })]
                    }))]
                })
            }))
        }
        );
        var $ = i(8915);
        const B = u.Ay.div`
    background-color: white;
    display: flex;
`
          , _ = u.Ay.div`
    transition: all 200ms ease;
    padding: 12px 24px;
    cursor: pointer;
    font: 500 14px Roboto;
    text-transform: uppercase;
    font-stretch: 100%;
    ${e => e.selected ? "\n        color: #000;\n        border-bottom: 2px solid rgb(51, 178, 168);\n    " : "\n        color: #ccc;\n        border-bottom: 2px solid white;\n    "}
`
          , z = ({onWriteDataItems: e, properties: t, AutoRendererOverrides: i}) => {
            const [a,s] = (0,
            r.useState)(0)
              , [l,c] = (0,
            r.useState)({
                content: (0,
                n.jsx)(n.Fragment, {}),
                visible: !1,
                title: ""
            })
              , u = (0,
            r.useRef)(null)
              , {translate: x} = (0,
            d.B)()
              , h = {
                dots: !1,
                infinite: !1,
                speed: 500,
                slidesToShow: 1,
                slidesToScroll: 1,
                beforeChange: (e, t) => s(t),
                arrows: !1
            };
            return (0,
            n.jsxs)(n.Fragment, {
                children: [(0,
                n.jsx)(p.aF, Object.assign({
                    visible: l.visible,
                    title: l.title,
                    onClose: () => c({
                        content: (0,
                        n.jsx)(n.Fragment, {}),
                        visible: !1,
                        title: ""
                    }),
                    layout: "CENTER"
                }, {
                    children: l.content
                })), (0,
                n.jsx)(B, Object.assign({
                    "data-testid": t.properties.key
                }, {
                    children: t.properties.tabs.map(( (e, t) => (0,
                    n.jsx)(_, Object.assign({
                        "data-testid": e.key,
                        selected: a === t,
                        onClick: () => (e => {
                            u.current && u.current.slickGoTo(e)
                        }
                        )(t)
                    }, {
                        children: x(e.title)
                    }), e.title)))
                })), (0,
                n.jsx)($.A, Object.assign({}, h, {
                    ref: u
                }, {
                    children: t.properties.tabs.map((t => (0,
                    n.jsx)("div", {
                        children: (0,
                        n.jsx)(o.V7, {
                            elements: t.elements,
                            setModal: c,
                            onWriteDataItems: e,
                            AutoRendererOverrides: i
                        })
                    }, t.title)))
                }))]
            })
        }
          , P = u.Ay.div`
    height: auto;
    transition: all 200ms ease;
    display: flex;
    align-items: center;
`
          , U = u.Ay.div`
    height: auto;
`
          , W = u.Ay.div`
    display: flex;
    flex-direction: column;
    font: 400 16px Roboto;
    align-items: left;
    height: 100%;
    padding: '16px';
    color: '#FFFFFF';
    margin-bottom: '16px';
    width: 100%;
`;
        u.Ay.div`
    justify-content: 'space-between';
    transition: all 200ms ease;
    display: flex;
    align-items: center;
`;
        var N = i(12902);
        const F = ({properties: e, onWriteDataItems: t, AutoRendererOverrides: i}) => {
            const {translate: a} = (0,
            d.B)()
              , s = ((0,
            N.DP)(),
            e.rows.filter(( () => !0)).filter((e => "string" !== typeof e)));
            return (0,
            n.jsx)(P, {
                children: (0,
                n.jsxs)(W, {
                    children: [(0,
                    n.jsx)(U, {
                        children: (0,
                        n.jsx)(p.o5, {
                            text: a(e.title),
                            size: "MEDIUM",
                            style: {
                                color: "#FFFFFF",
                                padding: "16px",
                                backgroundColor: "#004985"
                            },
                            face: "ROBOTO"
                        })
                    }), (0,
                    n.jsx)(o.V7, {
                        elements: s,
                        onWriteDataItems: t,
                        AutoRendererOverrides: i
                    })]
                })
            })
        }
        ;
        var Y = i(55043);
        const H = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;

    ${ ({inactive: e, readOnly: t, theme: i}) => e || t ? "\n    " : `\n    cursor: pointer;\n    @media only screen and (min-width: 0px) and (max-width: ${i.breakpoints.MEDIUM}px) {\n        cursor: default;\n    }\n\n    &:hover {\n        background-color: rgba(0, 0, 0, 0.05);\n    }\n    `}
`
          , V = u.Ay.div`
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
`
          , G = u.Ay.div`
    padding: 0;
`
          , Z = u.Ay.div`
    display: flex;
    font: 400 12px Roboto;
`
          , J = (u.Ay.img`
    height: 64px;
    width: 64px;
`,
        u.Ay.div`
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    height: 100%;
    padding: 0 32px 32px 32px;
    width: 100%;
`)
          , K = u.Ay.div`
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
`
          , q = ({active: e, direction: t, onClose: i, props: a}) => {
            const {translate: s, keys: o} = (0,
            d.B)()
              , [l,c] = (0,
            r.useState)({
                year: a.initialTime.year,
                month: a.initialTime.month,
                day: a.initialTime.day,
                hour: a.initialTime.hour,
                minute: a.initialTime.minute,
                second: a.initialTime.second
            });
            return (0,
            n.jsx)(p.rk, Object.assign({
                active: e,
                direction: t,
                title: s(o.TIME.DATE_AND_TIME),
                onClose: () => i(),
                footerElements: [(0,
                n.jsx)(p.$n, {
                    text: s(o.SAVE),
                    variant: "PRIMARY",
                    onClick: () => i(l)
                }, "confirm")]
            }, {
                children: (0,
                n.jsxs)(J, {
                    children: [(0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: (new Date).getFullYear(),
                            min: 2010,
                            value: l.year,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                year: e,
                                day: l.day <= new Date(l.year,l.month,0).getDate() ? l.day : new Date(l.year,l.month,0).getDate()
                            })),
                            description: s(o.TIME.YEAR)
                        })
                    }), (0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: 12,
                            min: 1,
                            value: l.month,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                month: e,
                                day: l.day <= new Date(l.year,e,0).getDate() ? l.day : new Date(l.year,e,0).getDate()
                            })),
                            description: s(o.TIME.MONTH)
                        })
                    }), (0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: new Date(l.year,l.month,0).getDate(),
                            min: 1,
                            value: l.day,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                day: e
                            })),
                            description: s(o.TIME.DAY)
                        })
                    }), (0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: 23,
                            min: 0,
                            value: l.hour,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                hour: e
                            })),
                            description: s(o.TIME.HOUR)
                        })
                    }), (0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: 59,
                            min: 0,
                            value: l.minute,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                minute: e
                            })),
                            description: s(o.TIME.MINUTE)
                        })
                    }), (0,
                    n.jsx)(K, {
                        children: (0,
                        n.jsx)(p.zp, {
                            max: 59,
                            min: 0,
                            value: l.second,
                            onChange: e => c(Object.assign(Object.assign({}, l), {
                                second: e
                            })),
                            description: s(o.TIME.SECOND)
                        })
                    })]
                })
            }))
        }
          , Q = ({onWriteDataItem: e, properties: t, readOnly: i, title: a, description: o}) => {
            const {translate: l, keys: c} = (0,
            d.B)()
              , {popStack: u, pushStack: x} = (0,
            s.hS)()
              , [h,m] = (0,
            r.useState)({
                year: (new Date).getFullYear(),
                month: (new Date).getMonth(),
                day: (new Date).getDay(),
                hour: (new Date).getHours(),
                minute: (new Date).getMinutes(),
                second: (new Date).getHours()
            });
            (0,
            r.useEffect)(( () => {
                if (t && t) {
                    const e = t.value.split("T")
                      , i = e[0]
                      , n = e[1]
                      , a = i.split("-")
                      , s = parseInt(a[0])
                      , o = parseInt(a[1])
                      , r = parseInt(a[2])
                      , l = n.split(":")
                      , d = parseInt(l[0])
                      , c = parseInt(l[1])
                      , p = parseInt(l[2]);
                    m({
                        year: s,
                        day: r,
                        hour: d,
                        minute: c,
                        month: o,
                        second: p
                    })
                }
            }
            ), [t]);
            return (0,
            n.jsx)(H, Object.assign({
                inactive: !1,
                readOnly: i,
                onClick: () => {
                    i || x({
                        component: q,
                        onClose: i => {
                            i && (i => {
                                const n = `${i.year}-${i.month < 10 ? `0${i.month}` : i.month}-${i.day < 10 ? `0${i.day}` : i.day}T ${i.hour < 10 ? `0${i.hour}` : i.hour}:${i.minute < 10 ? `0${i.minute}` : i.minute}:${i.second < 10 ? `0${i.second}` : i.second}`;
                                e(Object.assign(Object.assign({}, t), {
                                    value: n
                                }))
                            }
                            )(i),
                            u()
                        }
                        ,
                        props: {
                            initialTime: h
                        }
                    })
                }
            }, {
                children: (0,
                n.jsx)(V, {
                    children: (0,
                    n.jsx)(G, {
                        children: (0,
                        n.jsx)(Z, {
                            children: (0,
                            n.jsxs)("div", {
                                children: [(0,
                                n.jsx)(p.o5, {
                                    size: "SMALL_PLUS",
                                    text: l(a),
                                    face: "ROBOTO",
                                    type: "PRIMARY"
                                }), o && (0,
                                n.jsx)(p.o5, {
                                    size: "SMALL",
                                    text: l(o),
                                    face: "ROBOTO",
                                    type: "DISABLED",
                                    style: {
                                        margin: "4px 0 6px 0"
                                    }
                                }), (0,
                                n.jsx)(p.o5, {
                                    size: "SMALL",
                                    text: Y.A.format(new Date(t.value), "DD MMM YYYY HH:mm"),
                                    face: "ROBOTO",
                                    type: "DISABLED",
                                    style: {
                                        marginTop: "8px",
                                        cursor: "pointer"
                                    }
                                })]
                            })
                        })
                    })
                })
            }))
        }
        ;
        var X = i(91092)
          , ee = i(20767)
          , te = i(30318);
        const ie = u.Ay.div`
    height: auto;
    /* min-height: 72px; */
    padding: 16px;
    border-bottom: 2px solid #86a3a9;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    transition: all 200ms ease;

    ${ ({theme: e, inactive: t, readOnly: i}) => t || i ? "\n  " : `\n  cursor: pointer;\n  @media only screen and (min-width: 0px) and (max-width: ${e.breakpoints.MEDIUM}px) {\n      cursor: default;\n  }\n\n  &:hover {\n      background-color: rgba(0, 0, 0, 0.05);\n  }\n  `}
`
          , ne = u.Ay.div`
    white-space: normal;
    font: 400 14px Roboto;
    width: 100%;
`
          , ae = u.Ay.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
`
          , se = u.Ay.div`
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    width: 100%;
`
          , oe = ({props: e, active: t, direction: i, onClose: a}) => {
            const {translate: s, keys: o} = (0,
            d.B)()
              , [l,c] = (0,
            r.useState)({
                hour: e.hour,
                minute: e.minute
            });
            return (0,
            n.jsx)(p.rk, Object.assign({
                onClose: () => a(),
                active: t,
                direction: i,
                title: s(e.title),
                layout: "CENTER",
                footerElements: [(0,
                n.jsx)(p.$n, {
                    onClick: () => a(l),
                    text: s(o.OK),
                    variant: "PRIMARY"
                }, "write")]
            }, {
                children: (0,
                n.jsx)(ee.$, Object.assign({
                    dateAdapter: X.h
                }, {
                    children: (0,
                    n.jsxs)(se, {
                        children: [(0,
                        n.jsx)(p.o5, {
                            text: `\n                        ${e.min.hour < 10 ? "0" : ""}${e.min.hour} \n                        - \n                        ${e.max.hour < 10 ? "0" : ""}${e.max.hour}\n                        \n                        `,
                            size: "MEDIUM",
                            face: "INTER"
                        }), (0,
                        n.jsx)(te.a, {
                            onChange: t => {
                                c({
                                    hour: t.getHours(),
                                    minute: l.hour === e.max.hour ? 0 : t.getMinutes()
                                })
                            }
                            ,
                            value: new Date((new Date).getFullYear(),(new Date).getMonth(),(new Date).getDay(),l.hour,l.minute),
                            ampm: !1,
                            shouldDisableTime: (t, i) => {
                                if ("hours" === i) {
                                    if (e.max.hour < e.min.hour) {
                                        if (t.getHours() > e.max.hour && t.getHours() < e.min.hour)
                                            return !0
                                    } else if (t.getHours() > e.min.hour && t.getHours() < e.max.hour)
                                        return !0
                                } else if ("minutes" === i && t.getHours() === e.max.hour)
                                    return !0;
                                return !1
                            }
                        }), (0,
                        n.jsx)(p.o5, {
                            text: `${l.hour < 10 ? "0" : ""}${l.hour} : ${l.minute < 10 ? "0" : ""}${l.minute}`,
                            size: "LARGE_PLUS",
                            face: "INTER"
                        })]
                    })
                }))
            }))
        }
          , re = ({title: e, description: t, readOnly: i, properties: o, onWriteDataItem: l, testId: u}) => {
            const [x,h] = (0,
            r.useState)(o.value)
              , {translate: m} = (0,
            d.B)()
              , {popStack: g, pushStack: y} = (0,
            s.hS)();
            (0,
            r.useEffect)(( () => {
                h(o.value)
            }
            ), [o]);
            const v = x.hour
              , f = x.minute;
            return (0,
            n.jsx)(ie, Object.assign({
                inactive: !1,
                readOnly: i,
                "data-testid": u,
                onClick: () => {
                    i || y({
                        component: oe,
                        props: {
                            hour: o.value.hour,
                            minute: o.value.minute,
                            max: o.max,
                            min: o.min,
                            title: e
                        },
                        onClose: e => {
                            e && l(Object.assign(Object.assign({}, o), {
                                value: e
                            })),
                            g()
                        }
                    })
                }
            }, {
                children: (0,
                n.jsx)(ne, {
                    children: (0,
                    n.jsxs)(ae, {
                        children: [(0,
                        n.jsxs)("div", {
                            children: [(0,
                            n.jsx)(p.o5, {
                                text: m(e),
                                size: "SMALL_PLUS",
                                face: "ROBOTO",
                                type: "PRIMARY"
                            }), t && (0,
                            n.jsx)(p.o5, {
                                text: m(t),
                                size: "SMALL",
                                face: "ROBOTO",
                                style: {
                                    margin: "4px 0 6px 0"
                                }
                            }), (0,
                            n.jsx)(p.o5, {
                                text: `${v < 10 ? `0${v}` : v}:${f < 10 ? `0${f}` : f}`,
                                size: "SMALL_PLUS",
                                face: "ROBOTO",
                                style: {
                                    marginTop: "2px"
                                }
                            })]
                        }), i && (0,
                        n.jsx)(c.g, {
                            color: "#86a3a9",
                            "data-testid": "lock-icon",
                            icon: a.DW4
                        })]
                    })
                })
            }))
        }
        ;
        var le = i(51287);
        const de = u.Ay.div`
    display: flex;
    flex-direction: column;
    background-color: #fff;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 320px;
    z-index: 11;
    transition: all 300ms ease;
    box-shadow: 0px 2px 4px -1px rgb(0 0 0 / 20%), 0px 4px 5px 0px rgb(0 0 0 / 14%),
        0px 1px 10px 0px rgb(0 0 0 / 12%);

    @media only screen and (min-width: 0px) and (max-width: ${ ({theme: e}) => e.breakpoints.MEDIUM}px) {
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;

        ${e => e.open ? "\n                transform: translate3d(0%, 0, 0);\n        " : "\n                transform: translate3d(-101%, 0, 0);\n        "}
    }
`
          , ce = u.Ay.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    padding-left: 16px;
    background-color: #004985;
    color: #fff;
`
          , pe = u.Ay.div`
    overflow-y: auto;
    padding: 8px;
`
          , ue = u.Ay.div`
    display: flex;
    align-items: center;
`
          , xe = u.Ay.div`
    display: flex;
    align-items: center;
`
          , he = (u.Ay.img`
    width: 24px;
    height: 24px;
    cursor: pointer;
`,
        u.Ay.div`
    width: 32px;
    height: 32px;
    min-width: 32px;
    min-height: 32px;
    background-color: white;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    cursor: pointer;
`)
          , me = u.Ay.div`
    position: absolute;
    right: 6px;
    top: 8px;
    width: 10px;
    height: 10px;
    background-color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    border-radius: 50%;
`
          , ge = u.Ay.div`
    width: 8px;
    height: 8px;
    background-color: #e07f60;
    border-radius: 50%;
`
          , ye = (u.Ay.div`
    padding-left: 8px;
    padding-right: 8px;
    border-top: 1px solid #d3d3d3;
    width: 100%;
    margin: 16px 0;
`,
        u.Ay.div`
    background-color: white;
    color: #004985;
    border-radius: 50%;
    font-size: 14px;
    cursor: pointer;
    font-weight: bold;
    min-width: 32px;
    min-height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    &:hover {
        color: #666;
    }
    transition: all 200ms ease;
`);
        var ve;
        const fe = null !== (ve = window._env_.APP_VERSION) && void 0 !== ve ? ve : "3.0.0"
          , je = () => {
            switch (window.location.hostname) {
            case "localhost":
                return "- LOCALHOST";
            case "staging.savecair.heimdall-it.com":
                return "- STAGING";
            case "dev.savecair.heimdall-it.com":
                return "- DEV";
            default:
                return ""
            }
        }
          , be = ({menuItems: e, open: t}) => {
            const i = (0,
            r.useContext)(o.Es)
              , s = (0,
            l.Zp)();
            return (0,
            n.jsxs)(de, Object.assign({
                open: t
            }, {
                children: [(0,
                n.jsxs)(ce, {
                    children: [(0,
                    n.jsxs)("div", {
                        children: [(0,
                        n.jsx)(p.o5, {
                            text: "SAVE CONNECT",
                            type: "TRANSPARENT",
                            size: "MEDIUM_PLUS",
                            face: "INTER"
                        }), (0,
                        n.jsx)(p.o5, {
                            text: `${fe} ${je()}`,
                            type: "TRANSPARENT",
                            face: "INTER",
                            size: "SMALL_PLUS"
                        })]
                    }), !(null === i || void 0 === i ? void 0 : i.sandboxedDevice) && (0,
                    n.jsxs)(ue, {
                        children: [(0,
                        n.jsx)(xe, {
                            children: (0,
                            n.jsx)(le.Gv, {
                                onChange: e => {
                                    null === i || void 0 === i || i.updateAccount({
                                        input: {
                                            locale: null === e || void 0 === e ? void 0 : e.name
                                        }
                                    })
                                }
                                ,
                                overrideAppearance: e => (0,
                                n.jsx)(ye, {
                                    children: (0,
                                    n.jsx)(p.o5, {
                                        face: "INTER",
                                        size: "SMALL_PLUS",
                                        thickness: "BOLD",
                                        style: {
                                            color: "#004985",
                                            cursor: "pointer"
                                        },
                                        text: (null === e || void 0 === e ? void 0 : e.name.toUpperCase()) || ""
                                    })
                                })
                            })
                        }), (0,
                        n.jsxs)(he, Object.assign({
                            onClick: () => s("notifications")
                        }, {
                            children: [(0,
                            n.jsx)(c.g, {
                                icon: a.z$e,
                                color: "#004985",
                                size: "lg"
                            }), ((null === i || void 0 === i ? void 0 : i.notifications.edges) || []).filter((e => e.node.unread)).length > 0 && (0,
                            n.jsx)(me, {
                                children: (0,
                                n.jsx)(ge, {})
                            })]
                        }))]
                    })]
                }), (0,
                n.jsx)(pe, {
                    children: e
                })]
            }))
        }
        ;
        var Oe = i(59969)
          , Ae = function(e, t, i, n) {
            return new (i || (i = Promise))((function(a, s) {
                function o(e) {
                    try {
                        l(n.next(e))
                    } catch (t) {
                        s(t)
                    }
                }
                function r(e) {
                    try {
                        l(n.throw(e))
                    } catch (t) {
                        s(t)
                    }
                }
                function l(e) {
                    var t;
                    e.done ? a(e.value) : (t = e.value,
                    t instanceof i ? t : new i((function(e) {
                        e(t)
                    }
                    ))).then(o, r)
                }
                l((n = n.apply(e, t || [])).next())
            }
            ))
        };
        const we = () => {
            var e;
            const t = (0,
            r.useContext)(o.Es)
              , i = (0,
            l.zy)()
              , c = (0,
            l.Zp)()
              , p = (0,
            o.DV)()
              , {triggerToast2: u} = (0,
            s.dj)()
              , {reloadView: x} = (0,
            s.lQ)()
              , {translate: h, keys: g} = (0,
            d.B)();
            return t ? (0,
            n.jsx)(o.wI, {
                ConfigurationWizard: {
                    Content: Oe.uH,
                    title: h(g.NOTIFICATIONS.STARTUP_WIZARD)
                },
                AutoRendererOverrides: {
                    LinkElement: m,
                    PreviewGroupElement: b,
                    EnumDataElement: I,
                    NumberDataElement: E,
                    BooleanDataElement: C,
                    TabElement: z,
                    GroupElement: F,
                    HourMinuteDataElement: re,
                    DateTimeDataElement: Q
                },
                UpdateManager: Oe.f6,
                deviceId: t.selectedAccountDevice ? t.selectedAccountDevice.identifier : (null === (e = t.sandboxedDevice) || void 0 === e ? void 0 : e.deviceIdentifier) || "",
                CustomMenu: be,
                contentStyle: {
                    padding: "0px",
                    style: {
                        background: "linear-gradient(0deg, #c6dde1 0%, #cadede 55%, #cedfda 100%)"
                    }
                },
                menuItems: [{
                    active: i.pathname.includes("/device/home"),
                    onClick: () => c("home"),
                    title: h(g.VIEWS.HOME.TITLE),
                    icon: a.muz,
                    testId: "home"
                }, {
                    active: i.pathname.includes("/device/unit_information"),
                    onClick: () => c("unit_information"),
                    title: h(g.VIEWS.UNIT_INFORMATION.TITLE),
                    icon: a.mEO,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "unit_information"
                }, {
                    active: i.pathname.includes("/device/alarms"),
                    onClick: () => c("alarms"),
                    title: h(g.ALARMS.ALARMS),
                    icon: a.zpE,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "alarms"
                }, {
                    active: i.pathname.includes("/device/week_schedule"),
                    onClick: () => c("week_schedule"),
                    title: h(g.VIEWS.WEEK_SCHEDULE.TITLE),
                    icon: a.okg,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "week_schedule"
                }, {
                    active: i.pathname.includes("/device/filter"),
                    onClick: () => c("filter"),
                    title: h(g.FILTER.FILTER),
                    icon: a.mRM,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "filter"
                }, {
                    active: i.pathname.includes("/device/service"),
                    onClick: () => c("service"),
                    title: h(g.VIEWS.SERVICE.TITLE),
                    icon: a.h6r,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "service"
                }, {
                    active: i.pathname.includes("/device/help"),
                    onClick: () => c("help"),
                    title: h(g.HELP.TITLE),
                    icon: a.wRm,
                    disableWithoutConnection: !0,
                    hiddenWithoutConnection: !0,
                    testId: "help"
                }],
                routes: [{
                    path: "home",
                    element: (0,
                    n.jsx)(Oe.ww, {})
                }, {
                    path: "home/changeMode",
                    element: (0,
                    n.jsx)(Oe.bl, {})
                }, {
                    path: "home/change_airflow",
                    element: (0,
                    n.jsx)(Oe.LA, {})
                }, {
                    path: "home/change_temperature",
                    element: (0,
                    n.jsx)(Oe.ZE, {})
                }, {
                    path: "home/active_functions_home",
                    element: (0,
                    n.jsx)(Oe.sN, {})
                }, {
                    path: "service/password_settings/service_password",
                    element: (0,
                    n.jsx)(Oe.Sw, {})
                }, {
                    path: "unit_information/versions/update",
                    element: (0,
                    n.jsx)(Oe.jp, {})
                }, {
                    path: "week_schedule",
                    element: (0,
                    n.jsx)(Oe.E9, {})
                }, {
                    path: "week_schedule/edit",
                    element: (0,
                    n.jsx)(Oe.UB, {})
                }, {
                    path: "alarms/active",
                    element: (0,
                    n.jsx)(Oe.bD, {})
                }, {
                    path: "alarms/logs",
                    element: (0,
                    n.jsx)(Oe.JC, {})
                }, {
                    path: "service/backup",
                    element: (0,
                    n.jsx)(Oe.Uf, {})
                }, {
                    path: "filter",
                    element: (0,
                    n.jsx)(Oe.dJ, {})
                }, {
                    path: "service/trend_logs",
                    element: (0,
                    n.jsx)(Oe.vM, {})
                }],
                onWriteDataItems: (e, t="") => Ae(void 0, void 0, void 0, (function*() {
                    try {
                        const i = yield p(e, {
                            errorToast: !1
                        });
                        if (!i.success)
                            throw i.error;
                        x();
                        u({
                            severity: "success",
                            title: "Item updated successfully",
                            testId: "toast:write_success" + (t ? `:${t}` : "")
                        })
                    } catch (i) {
                        u({
                            severity: "error",
                            title: "Could not write data items"
                        })
                    }
                }
                ))
            }) : (0,
            n.jsx)("div", {})
        }
          , Ie = () => (0,
        n.jsx)(o.nM, Object.assign({
            blackListedRoutes: ["^/alarms/active", "^/account_settings", "^/device_linking", "^/add_device", "^/partners", "^/filter", "^/notifications"]
        }, {
            children: (0,
            n.jsx)(we, {})
        }))
    }
}]);
