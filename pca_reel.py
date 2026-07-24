"""
Principal Component Analysis — the directions that matter.
A tilted 3D point cloud has a shape; PCA finds its axes of greatest variance
(the eigenvectors of the covariance C v = lambda v), then drops the smallest
one and flattens the cloud onto the top-2 plane — 3D -> 2D keeping 96% of the
variance. Built with the manim-explainer-reel skill; every number is real
(eigen-decomposition of the actual sample covariance, seed 2).

Vertical 1080 x 1920 Instagram Reel layout (ThreeDScene):
  - top band    : gradient title + C v = lambda v  (+ covariance definition)
  - middle band : rotating 3D cloud, variance ellipsoid, principal axes, then
                  the collapse onto the PC1-PC2 plane
  - bottom band : projection z = V_k^T (x - xbar) + live variance-kept HUD
"""

from manim import *
import numpy as np

# ── Portrait 1080 × 1920 (Reels format) ─────────────────────────────────────
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30
config.background_color = "#000000"
config.disable_caching = True


class PCAReel(ThreeDScene):
    """PCA on a 110-point anisotropic 3D Gaussian (seed 2). Real covariance
    eigen-decomposition; the third component is dropped and the cloud flattens
    onto the plane of the top two, keeping 96% of the variance."""

    # ── Palette (fresh gradient: violet -> blue) ──────────────────────────────
    COL_TITLE_A = "#8B5CF6"   # violet
    COL_TITLE_B = "#3B82F6"   # blue
    COL_SUB     = "#B0B8D0"
    COL_PT      = "#60A5FA"   # data points (blue)
    COL_PC1     = "#FBBF24"   # 1st principal component (amber — most variance)
    COL_PC2     = "#FB7185"   # 2nd principal component (rose)
    COL_PC3     = "#64748B"   # 3rd component (slate — the one we drop)
    COL_ELL     = "#93C5FD"   # variance ellipsoid (faint)
    COL_DONE    = "#00FF88"   # quiet payoff green
    COL_EQ_BOX  = "#10102A"

    SC = 0.82                 # display scale for the cloud

    def construct(self):
        # =====================================================================
        # Real PCA (seed 2, pre-screened): 96% variance in the top 2 PCs
        # =====================================================================
        def Rx(t): c, s = np.cos(t), np.sin(t); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
        def Ry(t): c, s = np.cos(t), np.sin(t); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
        def Rz(t): c, s = np.cos(t), np.sin(t); return np.array([[c,-s,0],[s,c,0],[0,0,1]])

        rng = np.random.default_rng(2)
        sig = np.array([1.7, 0.9, 0.42])
        R = Rz(np.radians(38)) @ Rx(np.radians(28)) @ Ry(np.radians(16))
        P = (R @ (rng.normal(0, 1, (110, 3)) * sig).T).T
        P -= P.mean(0)
        C = np.cov(P.T)
        w, Vec = np.linalg.eigh(C)
        idx = np.argsort(w)[::-1]
        lam, V = w[idx], Vec[:, idx]                 # columns: PC1, PC2, PC3
        kept = 100 * (lam[0] + lam[1]) / lam.sum()   # ~96

        # PC coordinates and the projection onto the top-2 plane (drop PC3)
        coords = P @ V                               # (n,3) along PC1,PC2,PC3
        P_proj = coords[:, :2] @ V[:, :2].T          # flattened onto the plane

        def w3(p):                                   # world position, scaled
            return self.SC * np.array([p[0], p[1], p[2]])

        # camera that looks straight down the dropped axis (faces the plane)
        v3 = V[:, 2].copy()
        if v3[2] < 0:
            v3 = -v3
        face_phi = np.degrees(np.arccos(np.clip(v3[2], -1, 1)))
        face_theta = np.degrees(np.arctan2(v3[1], v3[0]))

        # =====================================================================
        # SECTION 1: Title band  — register each element before its animation
        # =====================================================================
        title = Tex("Principal Component Analysis", font_size=56)
        title.set_color_by_gradient(self.COL_TITLE_A, self.COL_TITLE_B)
        if title.width > 8.4:
            title.scale_to_fit_width(8.4)
        subtitle = Tex(r"\textit{finding the directions that matter}",
                       color=self.COL_SUB, font_size=33)
        title.to_edge(UP, buff=0.55)
        subtitle.next_to(title, DOWN, buff=0.2)

        eig_eq = MathTex(r"C\,", r"\mathbf{v}", r"=", r"\lambda\,", r"\mathbf{v}",
                         font_size=42, color=WHITE)
        eig_eq[1].set_color(self.COL_PC1)
        eig_eq[3].set_color(self.COL_TITLE_B)
        eig_eq[4].set_color(self.COL_PC1)
        eig_eq.next_to(subtitle, DOWN, buff=0.32)
        cov_note = MathTex(
            r"C = \tfrac{1}{n}\sum_i (\mathbf{x}_i - \bar{\mathbf{x}})"
            r"(\mathbf{x}_i - \bar{\mathbf{x}})^{\top}",
            font_size=27, color=self.COL_SUB)
        if cov_note.width > 8.2:
            cov_note.scale_to_fit_width(8.2)
        cov_note.next_to(eig_eq, DOWN, buff=0.22)

        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.2, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(FadeIn(subtitle, shift=DOWN * 0.2), run_time=0.8)
        self.add_fixed_in_frame_mobjects(eig_eq)
        self.play(Write(eig_eq), run_time=1.2)
        self.add_fixed_in_frame_mobjects(cov_note)
        self.play(FadeIn(cov_note), run_time=0.6)
        self.wait(0.3)

        # =====================================================================
        # SECTION 2: The 3D point cloud
        # =====================================================================
        self.set_camera_orientation(phi=70 * DEGREES, theta=-52 * DEGREES,
                                    zoom=0.82, frame_center=np.array([0, 0, 0.15]))
        world_axes = VGroup(*[
            Line(-1 * a, a, stroke_color="#2A3340", stroke_width=1.2).set_opacity(0.5)
            for a in (np.array([3.4, 0, 0]), np.array([0, 3.4, 0]),
                      np.array([0, 0, 3.4]))])
        self.add(world_axes)

        dots = VGroup(*[Dot3D(w3(p), radius=0.052, color=self.COL_PT,
                              resolution=(8, 8)) for p in P])

        def caption(tex_str, color=None):
            c = Tex(tex_str, font_size=31, color=color or self.COL_SUB)
            if c.width > 8.3:
                c.scale_to_fit_width(8.3)
            return c.move_to(np.array([0.0, -3.7, 0.0]))

        cap = caption(r"Data lives in 3D --- but it has a shape")
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0.0)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.012),
                  cap.animate.set_opacity(1.0), run_time=1.8)
        self.wait(0.3)

        # variance ellipsoid (2 sigma along each principal axis)
        rad = 2 * np.sqrt(lam)
        ell = Surface(
            lambda u, v: w3(V @ np.array([
                rad[0] * np.sin(u) * np.cos(v),
                rad[1] * np.sin(u) * np.sin(v),
                rad[2] * np.cos(u)])),
            u_range=[0, np.pi], v_range=[0, 2 * np.pi], resolution=(24, 24),
            fill_opacity=0.10, stroke_color=self.COL_ELL, stroke_width=0.4,
            stroke_opacity=0.3)
        ell.set_fill(self.COL_ELL, opacity=0.10)
        self.play(Create(ell), run_time=1.6)
        self.wait(0.3)

        # =====================================================================
        # SECTION 3: The principal axes (eigenvectors), longest = most variance
        # =====================================================================
        pc_cols = [self.COL_PC1, self.COL_PC2, self.COL_PC3]
        arrows, labels = VGroup(), VGroup()
        for i in range(3):
            end = w3(V[:, i] * rad[i])
            arr = Arrow3D(start=np.zeros(3), end=end, color=pc_cols[i],
                          thickness=0.02, base_radius=0.05)
            arrows.add(arr)
            lbl = MathTex(rf"\lambda_{i+1}{{=}}{lam[i]:.2f}",
                          font_size=26, color=pc_cols[i])
            lbl.next_to(end, UP, buff=0.05)
            labels.add(lbl)

        cap2 = caption(r"Principal components: the axes of greatest variance",
                       self.COL_PC1)
        self.add_fixed_in_frame_mobjects(cap2)
        cap2.set_opacity(0.0)
        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(GrowFromPoint(arrows[0], ORIGIN),
                  cap.animate.set_opacity(0.0), cap2.animate.set_opacity(1.0),
                  run_time=0.9)
        self.remove(cap)
        self.play(GrowFromPoint(arrows[1], ORIGIN),
                  GrowFromPoint(arrows[2], ORIGIN), run_time=0.8)
        for lbl in labels:
            self.add_fixed_orientation_mobjects(lbl)
        self.play(FadeIn(labels), run_time=0.6)
        self.wait(1.4)
        self.stop_ambient_camera_rotation()

        # =====================================================================
        # SECTION 4: Projection box + variance-kept HUD (bottom band)
        # =====================================================================
        proj_eq = MathTex(r"\mathbf{z}", r"=", r"V_k^{\top}",
                          r"(\mathbf{x} - \bar{\mathbf{x}})",
                          font_size=34, color=WHITE)
        proj_eq[0].set_color(self.COL_TITLE_B)
        proj_eq[2].set_color(self.COL_PC1)
        proj_eq.move_to(np.array([0.0, -4.95, 0.0]))
        proj_box = SurroundingRectangle(proj_eq, color=self.COL_TITLE_A,
                                        fill_color=self.COL_EQ_BOX, fill_opacity=0.8,
                                        buff=0.26, corner_radius=0.15, stroke_width=1.5)
        note = Tex(r"keep the top-$k$ components, drop the rest",
                   font_size=25, color=GREY_A).next_to(proj_box, DOWN, buff=0.26)
        var_label = Tex("variance kept:", font_size=32, color=GREY_A)
        var_num = Integer(0, font_size=32, color=GREY_A, unit=r"\%")
        var_hud = VGroup(var_label, var_num).arrange(RIGHT, buff=0.18
                                                     ).move_to([0.0, -6.7, 0])
        self.add_fixed_in_frame_mobjects(proj_box, proj_eq, note, var_hud)
        self.play(FadeIn(proj_box, shift=UP * 0.3), Write(proj_eq),
                  FadeIn(note), FadeIn(var_hud), run_time=1.3)
        self.wait(0.2)

        # =====================================================================
        # SECTION 5: Drop PC3 and flatten the cloud onto the top-2 plane
        # =====================================================================
        cap3 = caption(r"Drop the smallest --- flatten onto the top-2 plane",
                       self.COL_TITLE_B)
        self.add_fixed_in_frame_mobjects(cap3)
        cap3.set_opacity(0.0)
        self.play(arrows[2].animate.set_opacity(0.15),
                  labels[2].animate.set_opacity(0.15),
                  cap2.animate.set_opacity(0.0), cap3.animate.set_opacity(1.0),
                  run_time=0.7)
        self.remove(cap2)
        self.play(
            *[dots[i].animate.move_to(w3(P_proj[i])) for i in range(len(P))],
            ell.animate.set_opacity(0.0),
            arrows[2].animate.scale(0.01),
            ChangeDecimalToValue(var_num, int(round(kept))),
            run_time=2.0, rate_func=smooth)
        self.camera.add_fixed_in_frame_mobjects(var_num)   # re-pin (3D HUD gotcha)
        self.wait(0.4)

        # =====================================================================
        # SECTION 6: Face the plane — the 3D cloud becomes a 2D scatter
        # =====================================================================
        cap4 = caption(rf"3D $\rightarrow$ 2D, keeping {kept:.0f}\% of the variance",
                       self.COL_DONE)
        self.add_fixed_in_frame_mobjects(cap4)
        cap4.set_opacity(0.0)
        self.move_camera(phi=face_phi * DEGREES, theta=face_theta * DEGREES,
                         zoom=0.9, frame_center=np.array([0, 0, 0.0]),
                         added_anims=[cap3.animate.set_opacity(0.0),
                                      cap4.animate.set_opacity(1.0),
                                      FadeOut(world_axes)],
                         run_time=2.6)
        self.remove(cap3)
        # quiet 3B1B emphasis — variance number settles to green, no Flash
        self.play(var_num.animate.set_color(self.COL_DONE),
                  var_label.animate.set_color(self.COL_DONE), run_time=0.6)
        self.camera.add_fixed_in_frame_mobjects(var_num)
        self.play(dots.animate.set_color(self.COL_DONE), run_time=0.7)

        done = Tex("Dimensionality Reduced", font_size=36, color=self.COL_DONE
                   ).move_to([0.0, -7.45, 0.0])
        self.add_fixed_in_frame_mobjects(done)
        done.set_opacity(0.0)
        self.play(done.animate.set_opacity(1.0), run_time=0.9)
        self.wait(2.2)

        # =====================================================================
        # SECTION 7: Fade out
        # =====================================================================
        all_3d = VGroup(dots, ell, arrows, labels)
        all_2d = VGroup(title, subtitle, eig_eq, cov_note, cap4,
                        proj_box, proj_eq, note, var_hud, done)
        self.play(FadeOut(all_3d, shift=IN * 0.4),
                  FadeOut(all_2d, shift=DOWN * 0.3),
                  run_time=1.5, rate_func=smooth)
        self.wait(0.4)
