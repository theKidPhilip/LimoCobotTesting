from setuptools import find_packages, setup

package_name = 'wall_follower'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='aduasomaningnanakwaku@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'wall_follower = wall_follower.scripts.wall_follower:main',
            'wall_follower_pd  = wall_follower.scripts.wall_follower_pd:main',   
            'wall_follower_pid = wall_follower.scripts.wall_follower_pid:main',  
        ],
    },
)
