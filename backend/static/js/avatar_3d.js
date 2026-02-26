/**
 * Three.js 3D Avatar Animation System for ASL Translation
 * Handles loading, animating, and displaying a realistic 3D avatar
 * Supports Ready Player Me, MetaHuman, or standard GLTF/GLB models
 */

// Global variables
let scene, camera, renderer, avatar, mixer, clock;
let currentAnimations = [];
let handBones = null;
let isAvatarReady = false;

/**
 * Initialize the Three.js scene and avatar
 */
function initAvatarScene() {
    const container = document.getElementById('avatar3DContainer');
    if (!container) {
        console.error('Avatar container not found');
        return;
    }

    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Create camera
    camera = new THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    // Position for a chest-up view, common for ASL
    camera.position.set(0, 1.4, 1.5);
    camera.lookAt(0, 1.3, 0);

    // Create renderer
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance"
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    container.appendChild(renderer.domElement);

    // Add lighting (Studio style for better muscle/hand definition)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
    keyLight.position.set(2, 4, 5);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x4a90e2, 0.3);
    fillLight.position.set(-2, 2, 2);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
    rimLight.position.set(0, 2, -5);
    scene.add(rimLight);

    // Clock
    clock = new THREE.Clock();

    // Load avatar
    loadAvatar();

    // Window resize
    window.addEventListener('resize', onWindowResize, false);

    // Animation loop
    animate();

    console.log('✅ Realistic Avatar system initialized');
}

/**
 * Load avatar model
 */
function loadAvatar() {
    // Check if GLTFLoader is available
    if (typeof THREE.GLTFLoader === 'undefined') {
        console.warn('GLTFLoader not loaded, falling back to simple avatar');
        createSimpleAvatar();
        return;
    }

    const loader = new THREE.GLTFLoader();

    // Attempt to load the realistic avatar
    loader.load(
        '/static/models/avatar.glb',
        (gltf) => {
            avatar = gltf.scene;
            avatar.position.set(0, 0, 0);
            avatar.scale.set(1, 1, 1);

            // Enable shadows and sRGB
            avatar.traverse((node) => {
                if (node.isMesh) {
                    node.castShadow = true;
                    node.receiveShadow = true;
                    if (node.material.map) node.material.map.encoding = THREE.sRGBEncoding;
                }
            });

            scene.add(avatar);

            // Setup mixer
            mixer = new THREE.AnimationMixer(avatar);
            currentAnimations = gltf.animations;

            // Find bones for hand animations
            handBones = findHandBones(avatar);

            isAvatarReady = true;
            console.log('✅ Realistic avatar loaded successfully');
        },
        (progress) => {
            const percent = (progress.loaded / progress.total * 100).toFixed(0);
            console.log(`Loading avatar: ${percent}%`);
        },
        (error) => {
            console.warn('Error loading realistic avatar, falling back:', error.message);
            createSimpleAvatar();
        }
    );
}

/**
 * Find hand and finger bones in a standard humanoid rig (Mixamo/Xbot support)
 */
function findHandBones(model) {
    const bones = {
        leftHand: null,
        rightHand: null,
        leftArm: null,
        rightArm: null,
        leftForeArm: null,
        rightForeArm: null,
        leftFingers: {},
        rightFingers: {}
    };

    model.traverse((node) => {
        if (node.isBone) {
            const name = node.name.toLowerCase();

            // Mixamo naming convention (mixamorig...)
            if (name.includes('lefthand') || name.includes('left_hand')) bones.leftHand = node;
            if (name.includes('righthand') || name.includes('right_hand')) bones.rightHand = node;

            if (name.includes('leftarm') || name.includes('left_arm') || name.includes('leftshoulder')) bones.leftArm = node;
            if (name.includes('rightarm') || name.includes('right_arm') || name.includes('rightshoulder')) bones.rightArm = node;

            if (name.includes('leftforearm') || name.includes('left_fore_arm')) bones.leftForeArm = node;
            if (name.includes('rightforearm') || name.includes('right_fore_arm')) bones.rightForeArm = node;

            // Fingers
            const fingerNames = ['thumb', 'index', 'middle', 'ring', 'pinky'];
            fingerNames.forEach(finger => {
                if (name.includes(finger)) {
                    if (name.includes('left')) {
                        if (!bones.leftFingers[finger]) bones.leftFingers[finger] = [];
                        bones.leftFingers[finger].push(node);
                    } else if (name.includes('right')) {
                        if (!bones.rightFingers[finger]) bones.rightFingers[finger] = [];
                        bones.rightFingers[finger].push(node);
                    }
                }
            });
        }
    });

    return bones;
}

// ... (getASLAnimationData remains the same)

/**
 * Play keyframe-based procedural animation
 */
function playProceduralAnimation(data, callback) {
    const startTime = Date.now();
    const duration = data.duration * 1000;

    // Store initial rotations to reset later
    const initialRotations = {};
    if (handBones) {
        if (handBones.rightArm) initialRotations.rightArm = handBones.rightArm.quaternion.clone();
        if (handBones.rightForeArm) initialRotations.rightForeArm = handBones.rightForeArm.quaternion.clone();
        if (handBones.rightHand) initialRotations.rightHand = handBones.rightHand.quaternion.clone();
    }

    function frame() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Find keyframes
        const kfs = data.keyframes;
        let c = kfs[0], n = kfs[1] || kfs[0];

        for (let i = 0; i < kfs.length - 1; i++) {
            if (progress >= kfs[i].time / data.duration && progress < kfs[i + 1].time / data.duration) {
                c = kfs[i]; n = kfs[i + 1]; break;
            }
        }

        const t = (progress - c.time / data.duration) / ((n.time - c.time) / data.duration) || 0;
        const lerp = THREE.MathUtils.lerp;

        // Apply to REAL Bones (Mixamo Rig)
        if (handBones) {
            // Right Arm (Shoulder)
            if (handBones.rightArm && (c.rightArm?.rot || n.rightArm?.rot)) {
                const rotC = c.rightArm?.rot || { x: 0, y: 0, z: 0 };
                const rotN = n.rightArm?.rot || { x: 0, y: 0, z: 0 };

                handBones.rightArm.rotation.x = lerp(rotC.x || 0, rotN.x || 0, t);
                handBones.rightArm.rotation.z = lerp(rotC.z || 0, rotN.z || 0, t) - 1.5; // Offset for T-pose down
            }

            // Right Forearm (Elbow) - Infer from "Hand Pos" logic roughly? 
            // For now, simpler direct rotation control is better.

            // Right Hand (Wrist)
            if (handBones.rightHand && (c.rightHand?.pos || n.rightHand?.pos)) {
                // Approximate hand positioning via arm rotation/bend is hard inversely.
                // We will rotate the arm to "lift" the hand.
                // For simplicity in this procedural hacking:
                // If "pos.y" is high -> rotate shoulder up.
            }
        }

        // Apply to Simple Avatar (spheres)
        if (avatar.rightHand && !avatar.isGroup) { // Check if it's the simple mesh
            if (c.rightHand?.pos && n.rightHand?.pos) {
                avatar.rightHand.position.y = lerp(c.rightHand.pos.y, n.rightHand.pos.y, t);
                avatar.rightHand.position.z = lerp(c.rightHand.pos.z, n.rightHand.pos.z, t);
            }
        }

        if (progress < 1) {
            requestAnimationFrame(frame);
        } else {
            // Reset to idle (optional, or keep last frame)
            if (data.keyframes[data.keyframes.length - 1].reset && handBones) {
                // Smoothly return to T-pose or Idle?
                // For now just snap or leave it. 
            }
            callback();
        }
    }
    frame();
}

/**
 * Placeholder avatar
 */
function createSimpleAvatar() {
    avatar = new THREE.Group();
    const skinMat = new THREE.MeshPhongMaterial({ color: 0xffdbac });
    const clothMat = new THREE.MeshPhongMaterial({ color: 0x4a90e2 });

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.12, 32, 32), skinMat);
    head.position.y = 1.6;
    avatar.add(head);

    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 0.6, 32), clothMat);
    body.position.y = 1.2;
    avatar.add(body);

    // Arms and hands
    const armGeom = new THREE.CylinderGeometry(0.04, 0.04, 0.4, 16);

    avatar.leftArm = new THREE.Mesh(armGeom, skinMat);
    avatar.leftArm.position.set(-0.25, 1.25, 0);
    avatar.leftArm.rotation.z = Math.PI / 4;
    avatar.add(avatar.leftArm);

    avatar.rightArm = new THREE.Mesh(armGeom, skinMat);
    avatar.rightArm.position.set(0.25, 1.25, 0);
    avatar.rightArm.rotation.z = -Math.PI / 4;
    avatar.add(avatar.rightArm);

    avatar.rightHand = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 16), skinMat);
    avatar.rightHand.position.set(0.4, 1.05, 0);
    avatar.add(avatar.rightHand);

    scene.add(avatar);
    isAvatarReady = true;
    console.log('✅ Simple avatar fallback ready');
}

// Mouse interaction
let mouseX = 0;
let mouseY = 0;
let targetHeadRot = { x: 0, y: 0 };

document.addEventListener('mousemove', (event) => {
    // Normalize mouse coordinates (-1 to 1)
    mouseX = (event.clientX / window.innerWidth) * 2 - 1;
    mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
});

/**
 * Animation loop
 */
function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    const time = clock.getElapsedTime();

    if (mixer) {
        mixer.update(delta);
    } else if (avatar && isAvatarReady) {
        // Fallback procedural animation (Idle breathing & looking)
        animateSimpleAvatarIdle(time);
    }

    renderer.render(scene, camera);
}

function animateSimpleAvatarIdle(time) {
    if (!avatar) return;

    // Breathing (Chest expansion / vertical movement)
    const breath = Math.sin(time * 2) * 0.02;
    avatar.position.y = breath;

    // Head tracking (smoothly follow mouse)
    const head = avatar.children.find(c => c.geometry && c.geometry.type === 'SphereGeometry'); // Assuming head is sphere
    if (head) {
        // Target rotation limits
        const targetX = mouseY * 0.3; // Up/Down limit
        const targetY = mouseX * 0.6; // Left/Right limit

        // Smooth interpolation (lerp)
        head.rotation.x = THREE.MathUtils.lerp(head.rotation.x, targetX, 0.1);
        head.rotation.y = THREE.MathUtils.lerp(head.rotation.y, targetY, 0.1);
    }

    // Arms swaying slightly
    if (avatar.leftArm) {
        avatar.leftArm.rotation.z = (Math.PI / 4) + Math.cos(time * 1.5 + 1) * 0.05;
    }
    if (avatar.rightArm) {
        avatar.rightArm.rotation.z = (-Math.PI / 4) + Math.cos(time * 1.5) * 0.05;
    }
}

/**
 * Play ASL animation
 */
async function playASLAnimation(aslSign) {
    if (!isAvatarReady) return;

    console.log(`🎬 ASL Sign: ${aslSign}`);

    // Update UI
    const signNameEl = document.getElementById('currentSignName');
    if (signNameEl) signNameEl.innerText = aslSign;

    const signCharEl = document.getElementById('currentSignChar');
    if (signCharEl) signCharEl.innerText = aslSign.charAt(0);

    // Try to find GLTF animation clip first
    const clip = currentAnimations.find(a => a.name.toUpperCase() === aslSign.toUpperCase());

    if (clip && mixer) {
        return new Promise((resolve) => {
            const action = mixer.clipAction(clip);
            action.reset().setLoop(THREE.LoopOnce).play();
            const onFinished = () => {
                mixer.removeEventListener('finished', onFinished);
                resolve();
            };
            mixer.addEventListener('finished', onFinished);
        });
    } else {
        // Fallback to procedural keyframe animation
        const animData = getASLAnimationData(aslSign);
        if (animData) {
            return new Promise((resolve) => {
                playProceduralAnimation(animData, resolve);
            });
        } else {
            console.warn(`No animation data for: ${aslSign}`);
            await new Promise(r => setTimeout(r, 800)); // Default pause
        }
    }
}

/**
 * Procedural Animation Data
 */
function getASLAnimationData(aslSign) {
    const signs = {
        'HELLO': {
            duration: 1.2,
            keyframes: [
                { time: 0, rightArm: { rot: { z: -0.8, x: 0.5 } }, rightHand: { pos: { y: 1.4, z: 0.2 } }, fingers: { right: { index: 0.1, middle: 0.1 } } },
                { time: 0.4, rightArm: { rot: { z: -0.6, x: 0.7 } }, rightHand: { pos: { y: 1.55, z: 0.3 } }, fingers: { right: { index: 0, middle: 0 } } },
                { time: 1.2, reset: true }
            ]
        },
        'GOOD_MORNING': {
            duration: 1.2,
            keyframes: [
                { time: 0, rightArm: { rot: { z: -0.8, x: 0.5 } }, rightHand: { pos: { y: 1.4, z: 0.2 } }, fingers: { right: { index: 0.1, middle: 0.1 } } },
                { time: 0.4, rightArm: { rot: { z: -0.6, x: 0.7 } }, rightHand: { pos: { y: 1.55, z: 0.3 } }, fingers: { right: { index: 0, middle: 0 } } },
                { time: 1.2, reset: true }
            ]
        },
        'THANKS': {
            duration: 1.2,
            keyframes: [
                { time: 0, rightHand: { pos: { y: 1.4, z: 0.1 } }, fingers: { right: { all: 0 } } },
                { time: 0.5, rightHand: { pos: { y: 1.2, z: 0.4 } }, fingers: { right: { all: 0.2 } } },
                { time: 1.2, reset: true }
            ]
        },
        'PLEASE': {
            duration: 1.5,
            keyframes: [
                { time: 0, rightHand: { pos: { y: 1.3, z: 0.1 } }, rightArm: { rot: { x: 0.2 } } },
                { time: 0.5, rightArm: { rot: { x: 0.5 } } },
                { time: 1.0, rightArm: { rot: { x: 0.2 } } },
                { time: 1.5, reset: true }
            ]
        },
        'YES': {
            duration: 1.0,
            keyframes: [
                { time: 0, rightHand: { pos: { y: 1.2, z: 0.2 } } },
                { time: 0.3, rightHand: { pos: { y: 1.1, z: 0.2 } } },
                { time: 0.6, rightHand: { pos: { y: 1.2, z: 0.2 } } },
                { time: 1.0, reset: true }
            ]
        },
        'NO': {
            duration: 1.0,
            keyframes: [
                { time: 0, rightHand: { pos: { x: 0.4, y: 1.3 } } },
                { time: 0.3, rightHand: { pos: { x: 0.3, y: 1.3 } } },
                { time: 0.6, rightHand: { pos: { x: 0.4, y: 1.3 } } },
                { time: 1.0, reset: true }
            ]
        },
        'I': {
            duration: 1.0,
            keyframes: [
                { time: 0, rightHand: { pos: { x: 0, y: 1.3, z: 0.1 } } },
                { time: 0.5, rightHand: { pos: { x: 0, y: 1.2, z: 0.05 } } },
                { time: 1.0, reset: true }
            ]
        },
        'YOU': {
            duration: 1.0,
            keyframes: [
                { time: 0, rightHand: { pos: { x: 0.1, y: 1.4, z: 0.3 } } },
                { time: 0.5, rightHand: { pos: { x: 0.1, y: 1.4, z: 0.5 } } },
                { time: 1.0, reset: true }
            ]
        },
        '21': {
            duration: 1.8,
            keyframes: [
                // Start position - hand at chest level
                { time: 0, rightHand: { pos: { x: 0.3, y: 1.3, z: 0.2 } }, rightArm: { rot: { z: -0.3, x: 0.2 } }, fingers: { right: { index: 0, middle: 0, ring: 1, pinky: 1, thumb: 0.5 } } },
                // Show "2" - index and middle extended
                { time: 0.4, rightHand: { pos: { x: 0.35, y: 1.35, z: 0.25 } }, rightArm: { rot: { z: -0.4, x: 0.3 } }, fingers: { right: { index: 0, middle: 0, ring: 1, pinky: 1, thumb: 0.5 } } },
                // Hold "2"
                { time: 0.9, rightHand: { pos: { x: 0.35, y: 1.35, z: 0.25 } }, rightArm: { rot: { z: -0.4, x: 0.3 } }, fingers: { right: { index: 0, middle: 0, ring: 1, pinky: 1, thumb: 0.5 } } },
                // Transition to "1" - only index extended
                { time: 1.3, rightHand: { pos: { x: 0.32, y: 1.32, z: 0.22 } }, rightArm: { rot: { z: -0.35, x: 0.25 } }, fingers: { right: { index: 0, middle: 1, ring: 1, pinky: 1, thumb: 0.5 } } },
                // Hold "1"
                { time: 1.8, rightHand: { pos: { x: 0.32, y: 1.32, z: 0.22 } }, rightArm: { rot: { z: -0.35, x: 0.25 } }, fingers: { right: { index: 0, middle: 1, ring: 1, pinky: 1, thumb: 0.5 } } }
            ]
        }
    };
    return signs[aslSign.toUpperCase()];
}

/**
 * Play keyframe-based procedural animation
 */
function playProceduralAnimation(data, callback) {
    const startTime = Date.now();
    const duration = data.duration * 1000;

    function frame() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Find keyframes
        const kfs = data.keyframes;
        let c = kfs[0], n = kfs[1] || kfs[0];

        for (let i = 0; i < kfs.length - 1; i++) {
            if (progress >= kfs[i].time / data.duration && progress < kfs[i + 1].time / data.duration) {
                c = kfs[i]; n = kfs[i + 1]; break;
            }
        }

        const t = (progress - c.time / data.duration) / ((n.time - c.time) / data.duration) || 0;
        const lerp = THREE.MathUtils.lerp;

        // Apply to avatar (Simplified for base bones)
        if (avatar.rightHand) {
            if (c.rightHand?.pos && n.rightHand?.pos) {
                avatar.rightHand.position.y = lerp(c.rightHand.pos.y, n.rightHand.pos.y, t);
                avatar.rightHand.position.z = lerp(c.rightHand.pos.z, n.rightHand.pos.z, t);
            }
        }

        // Apply to bones if available
        if (handBones && handBones.rightHand) {
            // Complex bone interpolation would go here
        }

        if (progress < 1) {
            requestAnimationFrame(frame);
        } else {
            callback();
        }
    }
    frame();
}

/**
 * Sequence player
 */
async function playASLSequence(signs) {
    const progress = document.getElementById('animationProgress');
    for (let i = 0; i < signs.length; i++) {
        const sign = signs[i];
        if (progress) progress.style.width = ((i + 1) / signs.length * 100) + '%';
        await playASLAnimation(sign);
        await new Promise(r => setTimeout(r, 200));
    }
    if (progress) {
        setTimeout(() => {
            const signChar = document.getElementById('currentSignChar');
            const signName = document.getElementById('currentSignName');
            if (signChar) signChar.textContent = '✓';
            if (signName) signName.textContent = 'Animation terminée';
        }, 500);
    }
}

function onWindowResize() {
    const container = document.getElementById('avatar3DContainer');
    if (!container) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function resetAvatar() {
    location.reload();
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initAvatarScene, 100);
});
